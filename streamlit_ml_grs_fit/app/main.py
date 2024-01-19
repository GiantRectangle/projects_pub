import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pickle

def main():
    if 'grs_model' not in st.session_state:
        with open('rfr_model_bag.pkl','rb') as p:
            bag = pickle.load(p)
        st.session_state.df = bag['df']  
        st.session_state.grs_model = bag['grs_model']        
        st.session_state.grs_parameters = bag['grs_parameters']        
        st.session_state.gcs_model = bag['gcs_model']        
        st.session_state.gcs_parameters = bag['gcs_parameters']
    tab1, tab2, tab3 = st.tabs(['Form', 'GRs', 'GCs'])
    df = st.session_state.df        
    grs_parameters = st.session_state.grs_parameters
    gcs_parameters = st.session_state.gcs_parameters
    all_params = sorted(list(set(grs_parameters + gcs_parameters)))
    with tab1:
        with st.form('analysis_setup'):
            st.header('Random Forest Regression Machine Learning Model for Predicting GRs and GCs')
            st.subheader('Enter the following information (include burden, but not tax or insurance):')
            if 'df_project_inputs' not in st.session_state:
                st.session_state.placeholder_inputs = [14_370_022, 42_960, 610_265, 181_112, 827_359, 3_221_653, 173_953, 0]
            st.session_state.job_name = st.text_input(label='Project_name: ', value='MAGIC')
            st.session_state.df_project_inputs = pd.DataFrame(st.session_state.placeholder_inputs, index=all_params)
            st.session_state.df_project_inputs.index.names = ['PARAMETERS']
            st.session_state.edited_df_project_inputs = st.data_editor(st.session_state.df_project_inputs, use_container_width=True, disabled=("PARAMETERS",))
            st.session_state.edited_df_project_inputs = st.session_state.edited_df_project_inputs.T
            st.session_state.edited_grs_inputs = st.session_state.edited_df_project_inputs[grs_parameters]
            st.session_state.edited_gcs_inputs = st.session_state.edited_df_project_inputs[gcs_parameters]
            scale_factor_input = st.number_input(label='Scale Factor (number of projects above and below target): ', min_value=10, value=75, key='scale_factor')
            submit = st.form_submit_button('ANALYZE')
            if submit:
                with tab2:                    
                    target_name = 'GRS'
                    model = st.session_state.grs_model
                    fig1, details1, prediction = ModelAndScatterPlot(df, target_name, st.session_state.edited_grs_inputs, grs_parameters, model, scale_factor_input)
                    st.pyplot(fig1)
                    st.text(details1)
                with tab3:
                    target_name = 'GCS'
                    model = st.session_state.gcs_model
                    fig2, details2, prediction = ModelAndScatterPlot(df, target_name, st.session_state.edited_gcs_inputs, gcs_parameters, model, scale_factor_input)
                    st.pyplot(fig2)
                    st.text(details2)

def ModelAndScatterPlot(df_data, target_name, input_X, mask, model, scale_factor):

    # # set some varibles for use throughout
    graphWidth = 1500
    graphHeight = graphWidth * 800 / 1000
    job_name = st.session_state.job_name
    input_direct_cost = int(input_X['DIRECT_COST'])
    input_X = input_X[mask].values[0]
    feature_name = 'DIRECT COST'
    predictions_name = f'{target_name} PREDICTIONS'
    xData = np.array(df_data['DIRECT_COST'])
    yData = np.array(df_data[f'{target_name}_TRUE'])
    yPred = np.array(df_data[f'{target_name}_PREDICTIONS'])

    absError = yPred - yData
    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))

    # pare down df for vis
    over_val = df_data.DIRECT_COST.loc[df_data['DIRECT_COST'] >= input_direct_cost].to_list()
    over_val = sorted(over_val)
    under_val = df_data.DIRECT_COST.loc[df_data['DIRECT_COST'] < input_direct_cost].to_list()
    under_val = sorted(under_val, reverse=True)
    val_range = over_val[:scale_factor] + under_val[:scale_factor]
    df_working = df_data.loc[df_data['DIRECT_COST'].isin(val_range)]
    xData = np.array(df_working['DIRECT_COST'])
    yData = np.array(df_working[f'{target_name}_TRUE'])
    yPred = np.array(df_working[f'{target_name}_PREDICTIONS'])

    f = plt.figure(figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    axes = f.add_subplot(111)

    # first the raw data as a scatter plot
    axes.plot(xData, yData,  'o', alpha=0.3, label='actual data')

    # now the model as a scatter plot
    axes.scatter(xData, yPred, c='g', marker='*', label=f'{target_name} ml model')

    # now a test value
    prediction = model.predict([input_X])
    j, k = input_direct_cost, prediction
    plt.text(0.1, 0.8, f'{job_name}: {feature_name} = ${j:,.0f}',ha='left',va='top', weight='bold',transform = axes.transAxes)
    axes.scatter(j, k+RMSE, c='b', marker='D', label=f'{job_name}, {target_name} + σ')
    axes.annotate(f'{target_name} + σ = ${int(prediction)+RMSE:,.0f}', xy=(j, k+RMSE), xytext=(20,10), textcoords='offset points', arrowprops=dict(arrowstyle="->", color='black'))
    axes.scatter(j, k, c='k', marker='D', label=f'{job_name} Predicted {target_name}')
    axes.annotate(f'Predicted {target_name} = ${int(prediction):,.0f}', (j, k), xytext=(40,0), textcoords='offset points', arrowprops=dict(arrowstyle="->", color='black'))
    axes.scatter(j, k-RMSE, c='r', marker='D', label=f'{job_name}, {target_name} - σ')
    axes.annotate(f'{target_name} - σ = ${int(prediction)-RMSE:,.0f}', (j, k-RMSE), xytext=(20,-10), textcoords='offset points', arrowprops=dict(arrowstyle="->", color='black'))

    # labels and stuff
    axes.set_xlabel(feature_name)
    axes.set_ylabel(target_name)
    fmt = '${x:,.0f}'
    tick = StrMethodFormatter(fmt)
    axes.xaxis.set_major_formatter(tick)
    axes.yaxis.set_major_formatter(tick)
    axes.legend(loc='best')

    details = f'{job_name}: {feature_name} = ${input_direct_cost:,.0f}, Predicted {target_name}: ${int(prediction):,.0f}\n'+\
                        f'RMSE: {RMSE}\n'+\
                        f'R-squared: {Rsquared}'
    
    return f, details, prediction

if __name__ == '__main__':
    main()
