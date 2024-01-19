###############################################################
# title: snowflake_stored_procedure_test.py
# usage: foundation for python within snowflake.
# author: Swan Sodja
# description: should enable for and while loops required to apply addons
# system: python / snowflake
################################################################*/

import snowflake.connector
import pandas as pd
import json
from tabulate import tabulate
from snowflake.snowpark import Session

with open(r'..\..\..\Documents\Python Scripts\secrets.json') as f:
    scr = json.load(f)
sess = None
print('connecting...')
cnn_params = {
        'user' : scr['snowflake']['username']
        ,'password' : scr['snowflake']['password']
        ,'account' : scr['snowflake']['account']
        ,'warehouse' : 'dev_ts_admin_warehouse'
        ,'database' : 'sandbox'
        ,'schema' : 'trufflepig'
        ,'role' : 'techsolutions'
}
try:
    sess = Session.builder.configs(cnn_params).create()
    df_proj = sess.table('dr_sage_eid_mapping')
    df_name = df_proj.select('estimate_name').collect()
    for row in df_name:
        print(row)
    print('create procedure...')
    sql = ("create or replace procedure create_temp(from_table VARCHAR(16777216)) \n"
           "RETURNS VARCHAR(16777216)\n"
           "LANGUAGE PYTHON\n"
           "RUNTIME_VERSION = '3.8'\n"
           "packages = ('snowflake-snowpark-python')\n"
           "HANDLER = 'run'\n"
           "as\n"
           "$$\n"
           "def run(session, from_table):\n"
           "  to_table = str(from_table) + '_temp'\n"
           "  session.sql(f'create or replace transient table dr_sage_eid_mapping_temp as (select * from {from_table})').collect()\n"
           "  return('success!')\n"
           "$$;")
    result = sess.sql(sql)
    result.show()
    print('procedure created...')
    sql_call = "call create_temp('dr_sage_eid_mapping');"
    result = sess.sql(sql_call)
    result.show()
    print('procedure called...')
    df_new = sess.table('dr_sage_eid_mapping_temp')
    df_name_new = df_new.select('estimate_name').collect()
    for row in df_name_new:
        print(row)
except Exception as e:
    print(e)
finally:
    if sess:
        sess.close()
        print('connection closed...')
print('done.')


      
# if __name__ == '__main__':
#   df = output_estimate('2475')
#   print(df.info())