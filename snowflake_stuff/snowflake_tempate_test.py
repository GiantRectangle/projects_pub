###############################################################
# title: snowflake_apply_addons_test.py
# usage: building out the methods to be used within the stored procedure.
# author: Swan Sodja
# description: for and while loops required to apply addons
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
        ,'warehouse' : 'dev_ts_admin_warehouse'
        ,'database' : 'sandbox'
        ,'schema' : 'trufflepig'
        ,'role' : 'techsolutions'
}
try:
    print('session...')
    sess = Session.builder.configs(cnn_params).create()
    tbl = sess.sql('select project_name from dr_eos_ids;').collect()
    print('\r\n'.join(map(str, tbl))) 
except Exception as e:
    print(e)
finally:
    if sess:
        sess.close()
        print('connection closed...')
print('done.')
