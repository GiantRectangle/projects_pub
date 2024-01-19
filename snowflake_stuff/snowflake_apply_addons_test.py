###############################################################
# title: snowflake_apply_addons_test.py
# usage: building out the methods to be used within the stored procedure.
# author: Swan Sodja
# description: loops required to apply addons to each line within the items table. work in progress. still need to add the logic for the is_taxable flag. 
# system: python / snowflake
################################################################*/

import pandas as pd
import json
from tabulate import tabulate
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

with open(r'..\..\..\Documents\Python Scripts\secrets.json') as f:
    scr = json.load(f)

sess = None

print('connecting...')
cnn_params = {
        'user' : scr['snowflake']['username']
        ,'password' : scr['snowflake']['password']
        ,'account' : scr['snowflake']['account']
        ,'warehouse' : 'test_warehouse'
        ,'database' : 'sandbox'
        ,'schema' : 'trufflepig'
        ,'role' : 'techsolutions'
}
try:
    print('session...')
    sess = Session.builder.configs(cnn_params).create()
    def item(eid, table_suffix='', table_type='temporary', criteria_basis='', criteria_selection='', range_choice='', range_wbs_name='', min='', max=''):
        s = f'select * from table(select_project_items({eid}))'
        df_i = sess.create_dataframe(sess.sql(s).collect())
        if range_choice == 'P':   #---'P' is for phase, so here's where the min and max are bumpers for what phasecodes the addon gets applied to
            df_i = df_i.filter((col("PHASECODE") >= min) & (col("PHASECODE") <= max))
            # df_i.write.mode('overwrite').save_as_table(f'items_addons_{eid}_{table_suffix}', table_type=f'{table_type}')
        elif range_choice == 'W':   #---'W' is for wbs, so here's where the min and max are bumpers for what values to look for in the column pointed to in range_wbs_name
            df_wbs = wbs(eid, range_wbs_name)
            val_wbs = df_wbs.select(col('WBSCODE')).collect()[0].asDict()['WBSCODE']
            df_i = df_i.filter((col(val_wbs) >= min) & (col(val_wbs) <= max))
            # df_i.write.mode('overwrite').save_as_table(f'items_addons_{eid}_{table_suffix}', table_type=f'{table_type}')
        elif range_choice == '':   #---'' seems to mean it gets applied to everything
            # df_i.write.mode('overwrite').save_as_table(f'items_addons_{eid}_{table_suffix}', table_type=f'{table_type}')   #--- I think the write need to happen within the iteration. When it's here, it seems that it get's the whole table without the new column and then joins it to itself on each iteration
            df_i = df_i
        return df_i
    # item(eid=4694, table_suffix='base', table_type='temp', criteria_basis='C', criteria_selection='M', range_choice='W', range_wbs_name='SDI', min='0', max='2')
    # result_ia = sess.table('items_addons_4694_base').select(col('GLOBALROWIDENTIFIER'))
    # result_ia.show()
    def wbs(eid, range_wbs_name):   #---the wbs column name to use in the item table. comes from the range_wbs_name in a given addon
        s = f'select concat(\'wbs\',lpad((wbsindex + 1), 2, \'0\')) wbscode from dr_sage_estimates_wbsdefinition where  length(trim(description)) > 0 and estimateid = {eid} and description = \'{range_wbs_name}\''
        df_w = sess.create_dataframe(sess.sql(s).collect())
        return df_w
    # result_w = wbs(4694, 'SDI')
    # result_w.show()
    def addon(eid):   #---the list of all allocated addons for this project
        s = f'select * from table(select_project_allocated_addons({eid}))'
        df_a = sess.create_dataframe(sess.sql(s).collect())
        return df_a
    # result_a = addon(4694)
    # result_a.show()
    def each_addon(eid, desc):   #---set of allocated addons for this project, iterable by the list via the 2nd variable
        df_ea = addon(eid)
        df_ea = df_ea.filter(col("ADDON_DESC") == desc)
        return df_ea
    # result_ea = each_addon(4694, "Labor Burden")
    # result_ea.show()
    def cln(text):
        chars = ", \\`*_{}[]()>#+-.!$"
        for c in chars:
            text = text.replace(c, "")
        return text
    def iter_addon(eid):   #---iterating through the list of addons, and applying the rules to the correct lines in the item table
        item(eid, table_suffix='base', table_type='temp').write.mode('overwrite').save_as_table(f'items_addons_{eid}_base', table_type='temp')
        tblz = []
        df_base = sess.table(f'items_addons_{eid}_base')
        print('base table...')
        df_base.show()
        lst_a = [n.asDict()['ADDON_DESC'] for n in addon(eid).select(col('ADDON_DESC')).collect()]
        for i in lst_a:   #---everything works when run all together. 
            # if i == 'Special SDI on Subs':   #---this checks out when run by itself
            # if i == 'Special SDI on Select Material':   #---got it. it was dirty data in the source
            # if i == 'GR (T$9,016,192, RL$2,971,310)':   #---this checks out when run by itself
            # if i == 'Labor Burden':   #---this checks out when run by itself
                j = cln(i)
                df_a = each_addon(eid, i)
                criteria_basis = df_a.select(col('CRITERIABASIS')).collect()[0].asDict()['CRITERIABASIS'].strip()
                criteria_selection = df_a.select(col('CRITERIASELECTION')).collect()[0].asDict()['CRITERIASELECTION'].strip()
                rate = df_a.select(col('RATE')).collect()[0].asDict()['RATE']
                percent_or_dollar = df_a.select(col('PERCENTORDOLLAR')).collect()[0].asDict()['PERCENTORDOLLAR'].strip()
                range_choice = df_a.select(col('RANGECHOICE')).collect()[0].asDict()['RANGECHOICE'].strip()
                range_wbs_name = df_a.select(col('RANGEWBSNAME')).collect()[0].asDict()['RANGEWBSNAME'].strip()
                range_min_value = df_a.select(col('RANGEMINVALUE')).collect()[0].asDict()['RANGEMINVALUE'].strip()
                range_max_value = df_a.select(col('RANGEMAXVALUE')).collect()[0].asDict()['RANGEMAXVALUE'].strip()
                if any(c in 'E' for c in criteria_selection):
                    df_l = item(eid, f'E_{j}', 'temp', criteria_basis, criteria_selection, range_choice, range_wbs_name, range_min_value, range_max_value)   #---call the item table for this cost type for this addon
                    df_l = df_l.with_column(f'{i} - Equipment', col('EQPAMOUNT') * rate / 100).select(col('GLOBALROWIDENTIFIER'), col(f'{i} - Equipment'))   #---fliter the columns for the result and add calculated col for this cost type for this addon
                    print('table at iteration...')
                    df_l.write.mode('overwrite').save_as_table(f'items_addons_{eid}_E_{j}', table_type='temp')   #---create temp table for this cost type for this addon
                    df_l = sess.table(f'items_addons_{eid}_E_{j}')   #---grabs the temp table created above for this cost type for this addon
                    df_l.show()   #---console feedback top ten for this cost type for this addon
                    print('qc table at iteration...')
                    df_l.agg(f'{i} - Equipment', 'sum').show()   #---console feedback sum for this cost type for this addon
                    tblz.append(f'items_addons_{eid}_E_{j}')   #---append the table name for this cost type for this addon to the list of table names
                if any(c in 'L' for c in criteria_selection):
                    df_l = item(eid, f'L_{j}', 'temp', criteria_basis, criteria_selection, range_choice, range_wbs_name, range_min_value, range_max_value)   #---call the item table for this cost type for this addon
                    df_l = df_l.with_column(f'{i} - Labor', col('LABAMOUNT') * rate / 100).select(col('GLOBALROWIDENTIFIER'), col(f'{i} - Labor'))   #---fliter the columns for the result and add calculated col for this cost type for this addon
                    print('table at iteration...')
                    df_l.write.mode('overwrite').save_as_table(f'items_addons_{eid}_L_{j}', table_type='temp')   #---create temp table for this cost type for this addon
                    df_l = sess.table(f'items_addons_{eid}_L_{j}')   #---grabs the temp table created above for this cost type for this addon
                    df_l.show()   #---console feedback top ten for this cost type for this addon
                    print('qc table at iteration...')
                    df_l.agg(f'{i} - Labor', 'sum').show()   #---console feedback sum for this cost type for this addon
                    tblz.append(f'items_addons_{eid}_L_{j}')   #---append the table name for this cost type for this addon to the list of table names
                if any(c in 'M' for c in criteria_selection):
                    df_l = item(eid, f'M_{j}', 'temp', criteria_basis, criteria_selection, range_choice, range_wbs_name, range_min_value, range_max_value)   #---call the item table for this cost type for this addon
                    df_l = df_l.with_column(f'{i} - Material', col('MATAMOUNT') * rate / 100).select(col('GLOBALROWIDENTIFIER'), col(f'{i} - Material'))   #---fliter the columns for the result and add calculated col for this cost type for this addon
                    print('table at iteration...')
                    df_l.write.mode('overwrite').save_as_table(f'items_addons_{eid}_M_{j}', table_type='temp')   #---create temp table for this cost type for this addon
                    df_l = sess.table(f'items_addons_{eid}_M_{j}')   #---grabs the temp table created above for this cost type for this addon
                    df_l.show()   #---console feedback top ten for this cost type for this addon
                    print('qc table at iteration...')
                    df_l.agg(f'{i} - Material', 'sum').show()   #---console feedback sum for this cost type for this addon
                    tblz.append(f'items_addons_{eid}_M_{j}')   #---append the table name for this cost type for this addon to the list of table names
                if any(c in 'O' for c in criteria_selection):
                    df_l = item(eid, f'O_{j}', 'temp', criteria_basis, criteria_selection, range_choice, range_wbs_name, range_min_value, range_max_value)   #---call the item table for this cost type for this addon
                    df_l = df_l.with_column(f'{i} - Other', col('OTHAMOUNT') * rate / 100).select(col('GLOBALROWIDENTIFIER'), col(f'{i} - Other'))   #---fliter the columns for the result and add calculated col for this cost type for this addon
                    print('table at iteration...')
                    df_l.write.mode('overwrite').save_as_table(f'items_addons_{eid}_O_{j}', table_type='temp')   #---create temp table for this cost type for this addon
                    df_l = sess.table(f'items_addons_{eid}_O_{j}')   #---grabs the temp table created above for this cost type for this addon
                    df_l.show()   #---console feedback top ten for this cost type for this addon
                    print('qc table at iteration...')
                    df_l.agg(f'{i} - Other', 'sum').show()   #---console feedback sum for this cost type for this addon
                    tblz.append(f'items_addons_{eid}_O_{j}')   #---append the table name for this cost type for this addon to the list of table names
                if any(c in 'S' for c in criteria_selection):
                    df_l = item(eid, f'S_{j}', 'temp', criteria_basis, criteria_selection, range_choice, range_wbs_name, range_min_value, range_max_value)   #---call the item table for this cost type for this addon
                    df_l = df_l.with_column(f'{i} - Subcontract', col('SUBAMOUNT') * rate / 100).select(col('GLOBALROWIDENTIFIER'), col(f'{i} - Subcontract'))   #---fliter the columns for the result and add calculated col for this cost type for this addon
                    print('table at iteration...')
                    df_l.write.mode('overwrite').save_as_table(f'items_addons_{eid}_S_{j}', table_type='temp')   #---create temp table for this cost type for this addon
                    df_l = sess.table(f'items_addons_{eid}_S_{j}')   #---grabs the temp table created above for this cost type for this addon
                    df_l.show()   #---console feedback top ten for this cost type for this addon
                    print('qc table at iteration...')
                    df_l.agg(f'{i} - Subcontract', 'sum').show()   #---console feedback sum for this cost type for this addon
                    tblz.append(f'items_addons_{eid}_S_{j}')   #---append the table name for this cost type for this addon to the list of table names
        print(*tblz, sep='\r\n')
        for t in tblz:
            df_j = sess.table(t)
            print('table to join...')
            df_j.show()
            df_base = df_base.join(df_j, how='fullouter', on='GLOBALROWIDENTIFIER')
        df_base.write.mode('overwrite').save_as_table(f'items_addons_{eid}', table_type=f'transient')
        # sess.table(f'items_addons_{eid}').show()
    iter_addon(4694)
 
except Exception as e:
    print(e)
finally:
    if sess:
        sess.close()
        print('connection closed...')
print('done.')
