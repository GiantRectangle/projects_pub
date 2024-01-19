import streamlit as st
from snowflake import connector
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter
from scipy.optimize import curve_fit
import os
from os.path import join, dirname
from dotenv import load_dotenv

# get environment variables
dotenv_path = join(dirname('streamlit_grs_fit'), '.env')
load_dotenv(dotenv_path)
SF_ACCOUNT = os.getenv('SF_ACCOUNT')
SF_USER = os.getenv('SF_USER')
SF_PASSWORD = os.getenv('SF_PASSWORD')
SF_ROLE = os.getenv('SF_ROLE')
SF_WAREHOUSE = os.getenv('SF_WAREHOUSE')
SF_DATABASE = os.getenv('SF_DATABASE')
SF_SCHEMA = os.getenv('SF_SCHEMA')

# ignore any "invalid value in log" warnings internal to curve_fit() routine
import warnings
warnings.filterwarnings("ignore")

def main():
    with st.session_state():
        ...
    with st.cache_data():
        ...
    with st.form('analysis_setup'):
        with st.sidebar:
            fmt = '%d'
            st.header('GCs / GRs Least Squares Regression Model')
            st.subheader('Enter some info about the project you want to predict:')
            job_name = st.text_input(label='Project name for your project:', value='YOUR PROJECT NAME')
            direct_costs = st.number_input(label='Direct costs for your project:', value=14_000_000, format=fmt)
            st.subheader('Optionally, enter the GCs and GRs if known:')
            known_grs_costs = st.number_input(label='Known GRs Costs:', value=None)
            known_gcs_costs = st.number_input(label='Known GCs Costs:', value=None)
            st.subheader('Set the min and max for comparison (R-squared will go down when this is too tight, but the "saddle" of the prediction range will be wide if it\'s too loose):')
            min_total_costs = st.number_input(label='Minimum Total Costs:', value=100, format=fmt)
            max_total_costs = st.number_input(label='Maximum Total Costs:', value=500_000_000, format=fmt)
            submit = st.form_submit_button('ANALYSE')
    if submit:
        tab1, tab2, tab3 = st.tabs(['GRs', 'GCs', 'Table'])
        graphWidth = 1500
        graphHeight = graphWidth * 800 / 1000
        query = 'select '+\
            'job, gcs_cost, grs_cost, addons_cost, direct_cost, direct_labor_cost, total_cost '+\
            ',div0(gcs_cost, direct_cost) gcs_per_direct '+\
            ',div0(grs_cost, direct_cost) grs_per_direct '+\
            'from sandbox.public.gcs_fit '+\
            f'where total_cost >= {min_total_costs} '+\
            f'and total_cost <= {max_total_costs} '+\
            'and gcs_cost > 1000'
        df_data = load_data(query).set_index('JOB') 
        df_data = pd.DataFrame(df_data)
        df_data = df_data.loc[
                    (0.01 < df_data.TOTAL_COST) &
                    (0.01 < df_data.GCS_PER_DIRECT) & (df_data.GCS_PER_DIRECT < 500000) &
                    (0.01 < df_data.GRS_PER_DIRECT) & (df_data.GRS_PER_DIRECT < 500000) &
                    (df_data.GRS_COST < (50_000 + df_data.DIRECT_COST / 7))&
                    (df_data.GCS_COST < (50_000 + df_data.DIRECT_COST))
                ]
        df_grs = pd.DataFrame()
        df_grs['grs'] = df_data.GRS_COST
        df_grs['direct_cost'] = df_data.DIRECT_COST
        df_gcs = pd.DataFrame()
        df_gcs['gcs'] = df_data.GCS_COST
        df_gcs['direct_cost'] = df_data.DIRECT_COST
        # df_grs_gcs = pd.DataFrame()
        # df_grs_gcs['gcs'] = df_data.GCS_COST
        # df_grs_gcs['grs'] = df_data.GRS_COST
        with tab1:
            fig1, details1, grs_prediction = ModelAndScatterPlot(df_grs, graphWidth, graphHeight, job_name, direct_costs, known_grs_costs, known_gcs_costs)
            st.pyplot(fig1)
            st.text(details1)
        with tab2:
            fig2, details2, gcs_prediction = ModelAndScatterPlot(df_gcs, graphWidth, graphHeight, job_name, direct_costs, known_grs_costs, known_gcs_costs)
            st.pyplot(fig2)
            st.text(details2)
        with tab3:
            st.dataframe(df_data)

def func(x, a, b, c): # x-shifted log
    return a*np.log(x + b)+c

def ModelAndScatterPlot(df, graphWidth, graphHeight, job_name, input_costs, known_grs_costs=None, known_gcs_costs=None):
    feature_name = df.iloc[:,1:].columns[0].replace("_", " ").upper()
    target_name = df.iloc[:,0:1].columns[0].replace("_", " ").upper()
    xData = np.array(df.iloc[:,1])
    yData = np.array(df.iloc[:,0])

    # these are the same as the scipy defaults
    initialParameters = np.array([1.0, 1.0, 1.0])

    # curve fit the test data
    fittedParameters, pcov = curve_fit(func, xData, yData, initialParameters, maxfev=50000)
    modelPredictions = func(xData, *fittedParameters) 
    absError = modelPredictions - yData

    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    f = plt.figure(figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    axes = f.add_subplot(111)

    # first the raw data as a scatter plot
    axes.plot(xData, yData,  'o', alpha=0.3, label='actual data')

    # create data for the fitted equation plot
    xModel = np.linspace(min(xData), max(xData))
    yModel = func(xModel, *fittedParameters)

    # now the upper bound
    axes.plot(xModel, yModel + RMSE, c='b', alpha=0.5, linestyle='--', linewidth=0.7, label=f'{target_name} + σ')

    # now the model as a line plot
    axes.plot(xModel, yModel, c='g', linewidth=1, label=f'{target_name} ls regression')

    # now the lower bound
    axes.plot(xModel, yModel - RMSE, c='r', alpha=0.5, linestyle='--', linewidth=0.7, label=f'{target_name} - σ')

    # color +/- 1 std devialtion
    axes.fill_between(xModel, yModel + RMSE, yModel - RMSE, alpha=0.15)

    # now a test value
    prediction = fittedParameters[0] * np.log( input_costs + fittedParameters[1]) + fittedParameters[2]
    j, k = input_costs, prediction
    plt.text(0.1, 0.8, f'{job_name}: {feature_name} = ${input_costs:,.0f}',ha='left',va='top', weight='bold',transform = axes.transAxes)
    axes.scatter(j, k+RMSE, c='b', marker='D', label=f'{job_name}, {target_name} + σ')
    axes.annotate(f'{target_name} + σ = ${prediction+RMSE:,.0f}', (j+100, k+RMSE+100))
    axes.scatter(j, k, c='g', marker='D', label=f'{job_name} Predicted {target_name}')
    axes.annotate(f'Predicted {target_name} = ${prediction:,.0f}', (j+100, k+100))
    axes.scatter(j, k-RMSE, c='r', marker='D', label=f'{job_name}, {target_name} - σ')
    axes.annotate(f'{target_name} - σ = ${prediction-RMSE:,.0f}', (j+100, k-RMSE+100))

    #values if known
    if (target_name == 'GRS') & (known_grs_costs is not None):
        figure_check = f'Known {target_name} = ${known_grs_costs:,.0f}, prediction + {(known_grs_costs-prediction)/RMSE} * σ\n\n'
        h, i = input_costs, known_grs_costs
        axes.scatter(h, i, c='k', marker='D', label=f'{job_name} Known {target_name}')
    elif (target_name == 'GCS') & (known_gcs_costs is not None):
        figure_check = f'Known {target_name} = ${known_grs_costs:,.0f}, prediction + {(known_gcs_costs-prediction)/RMSE} * σ\n\n'
        o, p = known_grs_costs, known_gcs_costs
        axes.scatter(o, p, c='k', marker='D', label=f'{job_name} Known {target_name}')
    else:
        figure_check = '\n'

    # labels and stuff
    axes.set_xlabel(feature_name)
    axes.set_ylabel(target_name)
    fmt = '${x:,.0f}'
    tick = StrMethodFormatter(fmt)
    axes.xaxis.set_major_formatter(tick)
    axes.yaxis.set_major_formatter(tick)
    axes.legend(loc='lower right')

    details = f'{job_name}: {feature_name} = ${input_costs:,.0f}, Predicted {target_name}: ${prediction:,.0f}\n'+\
                        f'{figure_check}'+\
                        f'Parameters: {fittedParameters}\n'+\
                        f'Function:  {fittedParameters[0]} * ln( x + {fittedParameters[1]}) + {fittedParameters[2]}\n'+\
                        f'RMSE: {RMSE}\n'+\
                        f'R-squared: {Rsquared}'
    
    return f, details, prediction

def load_data(query):
    conn = connector.connect(
        user = SF_USER
        ,password = SF_PASSWORD
        ,account = SF_ACCOUNT
        ,warehouse = SF_WAREHOUSE
        ,database = SF_DATABASE
        ,schema = SF_SCHEMA
        ,role = SF_ROLE
    )
    cur = conn.cursor()
    df_data = cur.execute(query).fetch_pandas_all()
    return df_data

if __name__ == '__main__':
    main()