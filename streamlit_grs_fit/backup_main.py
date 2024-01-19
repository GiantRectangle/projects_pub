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
dotenv_path = join(dirname('streamlit_grs'), '.env')
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
    with st.form('analysis_setup'):
        with st.sidebar:
            fmt = '%d'
            st.header('GCs / GRs Least Squares Regression Model')
            st.subheader('Enter some info about the project you want to predict:')
            job_name = st.text_input(label='Project name for your project:', value='YOUR PROJECT NAME')
            direct_costs = st.number_input(label='Direct costs for your project:', value=14_000_000, format=fmt)
            st.subheader('Set up the data for comparison:')
            min_total_costs = st.number_input(label='Minimum Total Costs:', value=100_000, format=fmt)
            max_total_costs = st.number_input(label='Maximum Total Costs:', value=50_000_000, format=fmt)
            min_grs_ratio = st.slider(label='Minimum GRs Ratio (DIRECT_COST / GRS_COST):', min_value=0.05, max_value=0.25, value=0.2, step=0.05, format='%f')
            max_grs_ratio = st.slider(label='Maximum GRs Ratio (DIRECT_COST / GRS_COST):', min_value=500.0, max_value=600.0, value=500.7, step=0.1, format='%f')
            min_gcs_ratio = st.slider(label='Minimum GCs Ratio (DIRECT_COST / GCS_COST):', min_value=0.05, max_value=1.1, value=0.9, step=0.05, format='%f')
            max_gcs_ratio = st.slider(label='Maximum GCs Ratio (DIRECT_COST / GCS_COST):', min_value=90.0, max_value=110.0, value=100.7, step=0.1, format='%f')
            submit = st.form_submit_button('analyse')
    if submit:
        tab1, tab2, tab3 = st.tabs(['GRs', 'GCs', 'Table'])
        graphWidth = 1500
        graphHeight = graphWidth * 800 / 1000
        query = 'select '+\
            'job, gcs_cost, grs_cost, addons_cost, direct_cost, total_cost '+\
            'from dev_publish.public.gcs_fit '+\
            f'where direct_cost / gcs_cost >= {min_gcs_ratio} '+\
            f'and direct_cost / gcs_cost <= {max_gcs_ratio} '+\
            f'and direct_cost / grs_cost >= {min_grs_ratio} '+\
            f'and direct_cost / grs_cost <= {max_grs_ratio} '+\
            f'and total_cost >= {min_total_costs} '+\
            f'and total_cost <= {max_total_costs} '+\
            'and gcs_cost > 1000'
        df_data = load_data(query).set_index('JOB') 
        df_data = pd.DataFrame(df_data)
        with tab1:
            fig1, details1 = ModelAndScatterPlot(df_data, graphWidth, graphHeight, job_name, direct_costs, 'GRS_COST')
            st.pyplot(fig1)
            st.text(details1)
        with tab2:
            fig2, details2 = ModelAndScatterPlot(df_data, graphWidth, graphHeight, job_name, direct_costs, 'GCS_COST')
            st.pyplot(fig2)
            st.text(details2)
        with tab3:
            df_data['GCS_RATIO'] = df_data.DIRECT_COST / df_data.GCS_COST
            df_data['GRS_RATIO'] = df_data.DIRECT_COST / df_data.GRS_COST
            st.dataframe(df_data)

def func(x, a, b, c): # x-shifted log
    return a*np.log(x + b)+c

def ModelAndScatterPlot(frame, graphWidth, graphHeight, job_name, direct_costs, addon_name):
    df = frame

    target_table = f'{addon_name.upper()}'
    xData = np.array(df.DIRECT_COST)
    yData = np.array(df[target_table])

    # these are the same as the scipy defaults
    initialParameters = np.array([1.0, 1.0, 1.0])

    # curve fit the test data
    fittedParameters, pcov = curve_fit(func, xData, yData, initialParameters)
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
    axes.plot(xModel, yModel + RMSE, c='b', alpha=0.5, linestyle='--', linewidth=0.7, label=f'{addon_name} + σ')

    # now the model as a line plot
    axes.plot(xModel, yModel, c='g', linewidth=1, label=f'{addon_name} ls regression')

    # now the lower bound
    axes.plot(xModel, yModel - RMSE, c='r', alpha=0.5, linestyle='--', linewidth=0.7, label=f'{addon_name} - σ')

    # color +/- 1 std devialtion
    axes.fill_between(xModel, yModel + RMSE, yModel - RMSE, alpha=0.15)

    # now a test value
    job_name = job_name
    direct_costs = direct_costs
    addon = fittedParameters[0] * np.log( direct_costs + fittedParameters[1]) + fittedParameters[2]
    j, k = direct_costs, addon
    axes.scatter(j, k+RMSE, c='b', marker='D', label=f'{job_name}, {addon_name} + σ')
    axes.annotate(f'{addon_name} + σ = ${addon+RMSE:,.0f}', (j+100, k+RMSE+100))
    axes.scatter(j, k, c='g', marker='D', label=f'{job_name} Predicted {addon_name}')
    axes.annotate(f'Predicted {addon_name} = ${addon:,.0f}', (j+100, k+100))
    axes.scatter(j, k-RMSE, c='r', marker='D', label=f'{job_name}, {addon_name} - σ')
    axes.annotate(f'{addon_name} - σ = ${addon-RMSE:,.0f}', (j+100, k-RMSE+100))
    
    axes.set_xlabel('Direct Cost') # X axis data label
    axes.set_ylabel('Addon Cost') # Y axis data label
    fmt = '${x:,.0f}'
    tick = StrMethodFormatter(fmt)
    axes.xaxis.set_major_formatter(tick)
    axes.yaxis.set_major_formatter(tick)
    axes.legend(loc='lower right')

    details = f'{job_name}: Direct Costs = ${direct_costs:,.0f}, Predicted {addon_name}: ${addon:,.0f}\n\n'+\
                        f'Parameters: {fittedParameters}\n'+\
                        f'Function:  {fittedParameters[0]} * ln( x + {fittedParameters[1]}) + {fittedParameters[2]}\n'+\
                        f'RMSE: {RMSE}\n'+\
                        f'R-squared: {Rsquared}'
    return f, details

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