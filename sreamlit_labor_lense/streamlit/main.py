import os
import streamlit as st
from snowflake import connector
from snowflake.snowpark.context import get_active_session
import pandas as pd
import numpy as np
import re

st.set_page_config(
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'mailto:swans@sellen.com?subject=I Need Help',
         'Report a bug': "mailto:swans@sellen.com?subject=Bug Report!"
     }
 )

where_am_i = os.getenv('WHEREAMI')

def main():
    with st.sidebar:
            main_job_numbers = jobs_selection_parser(load_main_job_numbers().CONTRACT.to_list())
            selected_main_job_numbers = jobs_selection_parser(st.multiselect(label='Select Main Job Numbers', options=main_job_numbers))
            all_job_numbers = jobs_selection_parser(load_all_job_numbers().CONTRACT.to_list())
            available_sub_jobs = sub_job_parser(selected_main_job_numbers, all_job_numbers)
            selected_sub_job_numbers = jobs_selection_parser(st.multiselect(label='Select Sub Job Numbers', options=available_sub_jobs))
            selected_all_job_numbers = all_jobs_tuplizer(selected_main_job_numbers, selected_sub_job_numbers)
            st.caption('Selected Job Numbers:')
            st.text(selected_all_job_numbers)
            
    if selected_all_job_numbers:
        if where_am_i == 'THIS_ROBOT':
            query = f'select * from prod_publish.global.labor_lense where contract in {selected_all_job_numbers}'
        else:
            query = f'select * from code_schema.labor_lense_app_view where contract in {selected_all_job_numbers}'
        df_data = load_data(query)
        totals_df = total_df(df_data)
        crew_comp = crew_composition(df_data)
        tab1, tab2, tab3, tab4 = st.tabs(['Front Page', 'Additional Details', 'Export Main', 'Export Additional'])
        if isinstance(totals_df, pd.DataFrame):
            with tab1:
                st.caption('Labor Cost Per Hour:')
                st.dataframe(totals_df['LABOR_COST_PER_HOUR'].style.format('${:,.2f}'), use_container_width=True)

                st.caption('Burden Cost Percent of Labor:')
                st.dataframe(totals_df['BURDEN_COST_PRCT'].apply(lambda x: x * 100).style.format('{:.2f}%'), use_container_width=True)
                
                st.caption('Labor Percent of Job Total:')
                st.dataframe(totals_df['TRADE_PRCT_OF_JOB_TOTAL'].apply(lambda x: x * 100).style.format('{:.2f}%'), use_container_width=True)
                
                st.caption('Trade Percent of Craft Subtotal Labor Cost:')
                st.dataframe(totals_df['TRADE_PRCT_OF_CRAFT_SUBTOT'].dropna().apply(lambda x: x * 100).style.format('{:.2f}%'), use_container_width=True)
                
                st.caption('Trade Percent of Total Labor Cost:')
                st.dataframe(totals_df['TRADE_PRCT_OF_LABOR_TOTAL'].loc[~totals_df.index.get_level_values(0).isin(['Craft Subtotal', 'Grand Total'])].apply(lambda x: x * 100).style.format('{:.2f}%'), use_container_width=True)

                st.caption('OT / DT Percent by Trade:')
                st.dataframe(ovt_df(totals_df).apply(lambda x: x * 100).style.format('{:.2f}%'), height=600, use_container_width=True)

            with tab2:
                st.caption('Total Hours:')
                st.dataframe(totals_df['TOTAL_HOURS'].style.format('{:.2f}'), use_container_width=True)
                
                st.caption('Total Labor Cost:')
                st.dataframe(totals_df['LABOR_COST'].style.format('${:,.2f}'), use_container_width=True)
                
                st.caption('Total Burden Cost:')
                st.dataframe(totals_df['BURDEN_COST'].style.format('${:,.2f}'), use_container_width=True)
                
                st.caption('Total Dollars:')
                st.dataframe(df_data.groupby(by=['MAIN_CONTRACT']).agg({'LABOR_COST': 'sum', 'BURDEN_COST': 'sum', 'LINE_TOTAL_COST': 'sum'}).rename(columns={'LINE_TOTAL_COST': 'TOTAL_COST'}).style.format('${:,.2f}'), use_container_width=True)

                st.caption('Crew Composition:')
                st.dataframe(crew_comp.apply(lambda x: x * 100).style.format('{:.2f}%'), height=700, use_container_width=True)
                
            if where_am_i == 'THIS_ROBOT':
                with tab3:
                    totals_dfs, totals_code = spreadsheet(totals_df, df_names=['Totals'])
                    st.write(totals_dfs)
                    st.code(totals_code)
                with tab4:
                    comp_dfs, comp_code = spreadsheet(crew_comp, df_names=['Crew Composition'])
                    st.write(comp_dfs)
                    st.code(comp_code)
            else:
                with tab3:
                    st.dataframe(totals_df)
                with tab4:
                    st.dataframe(crew_comp)

def jobs_selection_parser(jobs_list):
    if isinstance(jobs_list, str):
        pat = r'[\(,\'\"\)]+'
        return str(re.sub(pat, '', jobs_list))
    elif isinstance(jobs_list, list):
        return tuple(jobs_list)
    else:
        return jobs_list
    
def sub_job_parser(main_jobs, jobs_list):
    sub_jobs_list = []
    if isinstance(main_jobs, str):
        for i in jobs_list:
            if i.startswith(main_jobs) & (i != main_jobs):
                sub_jobs_list.append(i)
    else:
        for _ in main_jobs:
            for i in jobs_list:
                if i.startswith(_) & (i != _):
                    sub_jobs_list.append(i)
    if len(sub_jobs_list) == 1:
        pat = r'[\[\],]+'
        return f"('{re.sub(pat, '',str(sub_jobs_list))}')"
    else:
        return tuple(sub_jobs_list)
    
def all_jobs_tuplizer(jobs, sub_jobs):
    all_jobs = ()
    for _ in (jobs, sub_jobs):
        try:
            if isinstance(_, str):
                all_jobs += (_,)
            else:
                all_jobs += _
        except TypeError:
            pass
    if len(all_jobs) == 1:
        pat = r'[,]+'
        all_jobs = re.sub(pat, '',str(all_jobs))
    return all_jobs

def ovt_df(df):
    df_ovt = df[['OVT_HRS_PRCT']]
    df_ovt.columns = df_ovt.columns.droplevel()
    ovt_index = [_*2+1 for _ in range(len(df_ovt.index))]
    df_ovt = df_ovt.reset_index()
    df_ovt.index = ovt_index
    df_ovt['ROLE'] = df_ovt['ROLE'].apply(lambda x: f'{x} OT')

    df_dt = df[['DT_HRS_PRCT']]
    df_dt.columns = df_dt.columns.droplevel()
    dt_index = [_*2+2 if _ > 0 else 2 for _ in range(len(df_dt.index))]
    df_dt = df_dt.reset_index()
    df_dt.index = dt_index
    df_dt['ROLE'] = df_dt['ROLE'].apply(lambda x: f'{x} DT')
    df_ovt_dt = pd.concat([df_ovt, df_dt])
    df_ovt_dt = df_ovt_dt.sort_index().set_index('ROLE')

    return df_ovt_dt

def crew_composition(df_data):
    frames_dict = {}
    idx=0
    for job in df_data['MAIN_CONTRACT'].unique():
        df_craft_dist = df_data.loc[(df_data['ROLE_L1'] == 'Craft') & (df_data['MAIN_CONTRACT'] == job)].groupby(by=['MAIN_CONTRACT', 'ROLE_L2', 'ROLE_L3']).agg({'TOTAL_HOURS': 'sum'})
        if not df_craft_dist.dropna().empty:
            df_craft_dist = df_craft_dist.groupby(level=(0,1), group_keys=True).apply(lambda x: x / float(x.iloc[:].sum()))
            df_craft_dist.index = df_craft_dist.index.droplevel([0,1])
            df_craft_dist = df_craft_dist.rename(columns={'TOTAL_HOURS':job})
            frames_dict[idx] = {}
            frames_dict[idx]['job'] = job
            frames_dict[idx]['df'] = df_craft_dist
            idx+=1
    frames_list = [frames_dict[k]['df'] for k,v in frames_dict.items()]
    if len(frames_list) >= 2:
        merge_df = pd.merge(how='outer', left=frames_list[0], right=frames_list[1], on=['ROLE_L2', 'ROLE_L3'])
        for _ in range(len(frames_list[2:])):
            merge_df = pd.merge(how='outer', left=merge_df, right=frames_list[2+_], on=['ROLE_L2', 'ROLE_L3'])
        return merge_df
    elif len(frames_list) == 1:
        return frames_list[0]
    else:
        return None

def total_df(df_data):
    df_data = pd.DataFrame(df_data)
    if not df_data.dropna().empty:
        df_craft = df_data.loc[df_data['ROLE_L1'] == 'Craft'].groupby(by=['MAIN_CONTRACT', 'ROLE_L2']).agg({'TOTAL_HOURS': 'sum', 'REG_HOURS': 'sum', 'OVT_HOURS': 'sum', 'DT_HOURS': 'sum', 'LABOR_COST': 'sum', 'BURDEN_COST': 'sum', 'LINE_TOTAL_COST': 'sum'})
        df_craft = df_craft.reset_index()
        df_craft['LABOR_COST_PER_HOUR'] = df_craft.LABOR_COST / df_craft.TOTAL_HOURS
        df_craft['BURDEN_COST_PRCT'] = df_craft.BURDEN_COST / df_craft.LABOR_COST
        df_craft['REG_HRS_PRCT'] = df_craft.REG_HOURS / df_craft.TOTAL_HOURS
        df_craft['OVT_HRS_PRCT'] = df_craft.OVT_HOURS / df_craft.TOTAL_HOURS
        df_craft['DT_HRS_PRCT'] = df_craft.DT_HOURS / df_craft.TOTAL_HOURS
        df_craft = df_craft.pivot(index='ROLE_L2', columns='MAIN_CONTRACT', values=['TOTAL_HOURS', 'LABOR_COST', 'LABOR_COST_PER_HOUR', 'BURDEN_COST', 'BURDEN_COST_PRCT', 'REG_HRS_PRCT', 'OVT_HRS_PRCT', 'DT_HRS_PRCT', 'LINE_TOTAL_COST'])
        df_craft = df_craft.reset_index(names='ROLE')
        df_craft['ROLE'] = df_craft['ROLE'].apply(lambda x: f'{x} Composite Crew')
        for _ in df_craft['LABOR_COST'].columns:
            df_craft['TRADE_PRCT_OF_CRAFT_SUBTOT', _] = df_craft['LABOR_COST', _] / df_craft['LABOR_COST', _].sum()

        df_subtotals = df_data.loc[df_data.TOTAL_HOURS != 0].groupby(by=['MAIN_CONTRACT', 'ROLE_L1']).agg({'TOTAL_HOURS': 'sum', 'REG_HOURS': 'sum', 'OVT_HOURS': 'sum', 'DT_HOURS': 'sum', 'LABOR_COST': 'sum', 'BURDEN_COST': 'sum', 'LINE_TOTAL_COST': 'sum'})
        df_subtotals = df_subtotals.reset_index()
        df_subtotals['LABOR_COST_PER_HOUR'] = df_subtotals.LABOR_COST / df_subtotals.TOTAL_HOURS
        df_subtotals['BURDEN_COST_PRCT'] = df_subtotals.BURDEN_COST / df_subtotals.LABOR_COST
        df_subtotals['REG_HRS_PRCT'] = df_subtotals.REG_HOURS / df_subtotals.TOTAL_HOURS
        df_subtotals['OVT_HRS_PRCT'] = df_subtotals.OVT_HOURS / df_subtotals.TOTAL_HOURS
        df_subtotals['DT_HRS_PRCT'] = df_subtotals.DT_HOURS / df_subtotals.TOTAL_HOURS
        df_subtotals = df_subtotals.pivot(index='ROLE_L1', columns='MAIN_CONTRACT', values=['TOTAL_HOURS', 'LABOR_COST', 'LABOR_COST_PER_HOUR', 'BURDEN_COST', 'BURDEN_COST_PRCT', 'REG_HRS_PRCT', 'OVT_HRS_PRCT', 'DT_HRS_PRCT', 'LINE_TOTAL_COST'])
        df_subtotals = df_subtotals.reset_index(names='ROLE')
        df_subtotals['ROLE'] = df_subtotals['ROLE'].apply(lambda x: f'{x} Subtotal')

        df_total = df_data.groupby(by=['MAIN_CONTRACT']).agg({'TOTAL_HOURS': 'sum', 'REG_HOURS': 'sum', 'OVT_HOURS': 'sum', 'DT_HOURS': 'sum', 'LABOR_COST': 'sum', 'BURDEN_COST': 'sum', 'LINE_TOTAL_COST': 'sum'})
        df_total = df_total.reset_index()
        df_total['ROLE'] = 'Grand Total'
        df_total['LABOR_COST_PER_HOUR'] = df_total.LABOR_COST / df_total.TOTAL_HOURS
        df_total['BURDEN_COST_PRCT'] = df_total.BURDEN_COST / df_total.LABOR_COST
        df_total['REG_HRS_PRCT'] = df_total.REG_HOURS / df_total.TOTAL_HOURS
        df_total['OVT_HRS_PRCT'] = df_total.OVT_HOURS / df_total.TOTAL_HOURS
        df_total['DT_HRS_PRCT'] = df_total.DT_HOURS / df_total.TOTAL_HOURS
        df_total = df_total.pivot(index='ROLE', columns='MAIN_CONTRACT', values=['TOTAL_HOURS', 'LABOR_COST', 'LABOR_COST_PER_HOUR', 'BURDEN_COST', 'BURDEN_COST_PRCT', 'REG_HRS_PRCT', 'OVT_HRS_PRCT', 'DT_HRS_PRCT', 'LINE_TOTAL_COST'])
        df_total = df_total.reset_index(names='ROLE')
        df = pd.concat([df_craft, df_subtotals, df_total])
        df.columns.name = 'HOURS'
        df = df.reset_index(drop=True).set_index('ROLE')
        for _ in df['LABOR_COST'].columns:
            labor_total = df['LABOR_COST', _].loc[~df.index.get_level_values(0).isin(['Craft Subtotal', 'Grand Total'])].sum()
            df['TRADE_PRCT_OF_LABOR_TOTAL', _] = df['LABOR_COST', _] / labor_total
        for _ in df['LABOR_COST'].columns:
            grand_total = df['LINE_TOTAL_COST', _].loc[df.index.get_level_values(0).isin(['Grand Total'])].sum()
            df['TRADE_PRCT_OF_JOB_TOTAL', _] = df['LABOR_COST', _] / grand_total
        return df
    else:
        return None

def sort_options(lst):
    return list(lst).sort()

if where_am_i == 'THIS_ROBOT':
    from mitosheet.streamlit.v1 import spreadsheet
    import json
    with open(r'C:\Users\SwanS\projects\secrets.json') as f:
        scr = json.load(f)

    SF_ACCOUNT = scr['snowflake']['account']
    SF_USER = scr['snowflake']['username']
    SF_PASSWORD = scr['snowflake']['password']
    SF_ROLE = scr['snowflake']['role']
    SF_WAREHOUSE = scr['snowflake']['warehouse']
    SF_DATABASE = 'dev_publish'
    SF_SCHEMA = 'global'

    def load_data(query):
        cur = create_connection()
        df_data = cur.execute(query).fetch_pandas_all()
        return df_data

    @st.cache_data
    def load_all_job_numbers():
        all_jn_query = 'select distinct contract from prod_publish.global.labor_lense order by contract'
        cur = create_connection()
        df_data = cur.execute(all_jn_query).fetch_pandas_all()
        return df_data

    @st.cache_data
    def load_main_job_numbers():
        main_jn_query = 'select distinct split_part(contract, \'.\', 1) contract from prod_publish.global.labor_lense order by contract'
        cur = create_connection()
        df_data = cur.execute(main_jn_query).fetch_pandas_all()
        return df_data

    @st.cache_resource
    def create_connection():
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
        cur.execute('use warehouse prod_ts_elt_warehouse;')
        return cur
else:
    def load_data(query):
        session = get_active_session()
        data = session.sql(query).collect()
        created_dataframe = session.create_dataframe(data)
        df_data = created_dataframe.to_pandas()
        return df_data
    
    def load_all_job_numbers():
        for attempt in range(10):
            try:
                all_jn_query = 'select distinct contract from code_schema.labor_lense_app_view order by contract'
                session = get_active_session()
                data = session.sql(all_jn_query).collect()
                created_dataframe = session.create_dataframe(data)
                df_data = created_dataframe.to_pandas()
            except ValueError:
                continue
            else:
                break
        print('Something went wrong. Please restart the app')
        return df_data

    def load_main_job_numbers():
        for attempt in range(10):
            try:
                main_jn_query = 'select distinct split_part(contract, \'.\', 1) contract from code_schema.labor_lense_app_view order by contract'
                session = get_active_session()
                data = session.sql(main_jn_query).collect()
                created_dataframe = session.create_dataframe(data)
                df_data = created_dataframe.to_pandas()
            except ValueError:
                continue
            else:
                break
        print('Something went wrong. Please restart the app')
        return df_data

if __name__ == '__main__':
    main()