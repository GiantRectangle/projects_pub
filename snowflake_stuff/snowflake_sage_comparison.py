###############################################################
# title: snowflake_sage_comparison.py
# usage: compares row counts between tables in sage to the same table in snowflake.
# author: Swan Sodja
# description: opperator will have to have their secrets.json in position, or otherwise provide the infor to the variables in snowflake connections.
#              opperator will need to establish an odbc connector called sage_estimates connected to sage with their credentials
# system: python
################################################################*/

import snowflake.connector
import pandas as pd
import json
import pyodbc

# sage connections
cxn = pyodbc.connect('DSN=sage_estimates')
crs_s = cxn.cursor() 

# snowflake connections
with open(r'..\..\..\Documents\Python Scripts\secrets.json') as f:
    scr = json.load(f)
usr = scr['snowflake']['username']
pwd = scr['snowflake']['password']
act = scr['snowflake']['account']
whse = scr['snowflake']['warehouse']
dbse = 'DEV_RAW'   # scr['snowflake']['database']
scma = 'SAGE'   # scr['snowflake']['schema']
rle = scr['snowflake']['role']
con = snowflake.connector.connect(
        user=f'{usr}'
        ,password=f'{pwd}'
        ,account=f'{act}'
        ,warehouse=f'{whse}'
        ,database=f'{dbse}'
        ,schema=f'{scma}'
        ,role=f'{rle}'
      )
crs = con.cursor()

# navigaion and mapping between sage and snowflake
tbls = { 'estimates' : { 'addon' : { 'snowflake' : 'ESTIMATES_ADDON'
                                    ,'sage' : 'Estimates.Secured.Addon' }
                        ,'estimate' : { 'snowflake' : 'ESTIMATES_ESTIMATE'
                                    ,'sage' : 'Estimates.Secured.Estimate' }
                        ,'item' : { 'snowflake' : 'ESTIMATES_ITEM'
                                    ,'sage' : 'Estimates.Secured.Item' }
                        ,'phase' : { 'snowflake' : 'ESTIMATES_PHASE'
                                    ,'sage' : 'Estimates.Secured.Phase' }
                        ,'wbsdefinition' : { 'snowflake' : 'ESTIMATES_WBSDEFINITION'
                                    ,'sage' : 'Estimates.Secured.WbsDefinition' }
                        ,'projectinfo' : { 'snowflake' : 'ESTIMATES__PROJECTINFO'
                                    ,'sage' : 'Estimates.Secured._ProjectInfo' }
    }
        ,'livedb' : { 'addon' : { 'snowflake' : 'LIVE_ADDON'
                                    ,'sage' : 'Live_Database.dbo.Addon' }
                        ,'addonbasis' : { 'snowflake' : 'LIVE_ADDONBASIS'
                                    ,'sage' : 'Live_Database.dbo.AddonBasis' }
                        ,'item' : { 'snowflake' : 'LIVE_ITEM'
                                    ,'sage' : 'Live_Database.dbo.Item' }
                        ,'unit' : { 'snowflake' : 'LIVE_UNIT'
                                    ,'sage' : 'Live_Database.dbo.Unit' }
                        ,'wbsdefinition' : { 'snowflake' : 'LIVE_WBSDEFINITION'
                                    ,'sage' : 'Live_Database.dbo.WbsDefinition' }
    }
} 
dbs = list(tbls.keys())
names = sum([list(tbls[i].keys()) for i in dbs], [])

def dict_caller(dbse, nm, prgm):
    our_tbls = []
    for db in tbls.items():
        db = dict([db])
        db = dict((k, db[k]) for k in [dbse] if k in db)
        for name in db.values():
            name = dict((k, name[k]) for k in [nm] if k in name)
            for tbl in name.values():
                our_tbls += list(dict((k, tbl[k]) for k in [prgm] if k in tbl).values())
    return our_tbls

def sage_list_caller(dbse, nm):
  sage_table = dict_caller(dbse, nm, 'sage')
  return sage_table[0]

def snowflake_list_caller(dbse, nm):
    sage_table = dict_caller(dbse, nm, 'snowflake')
    return sage_table[0]

def count_rows():
  df = pd.DataFrame()
  df2 = pd.DataFrame()
  df3 = pd.DataFrame()
  for d in dbs:
    for n in names:
      try:
        sage_tbl = sage_list_caller(d,n)
        snowflake_tbl = snowflake_list_caller(d,n)
        sage_qry = f'select count(*) from {sage_tbl}'
        snowflake_qry = f'select count(*) from {snowflake_tbl}'
        crs_s.execute(sage_qry)
        crs.execute(snowflake_qry)
        df3['sage_row_count'] = crs_s.fetchall()
        df3['sage_row_count'] = df3['sage_row_count'].str[0].astype(int)
        df3['database'] = f'{d}'
        df3['name'] = f'{n}'
        df2['snowflake_row_count'] = crs.fetchone()
        df2['database'] = f'{d}'
        df2['name'] = f'{n}'
        df_m = pd.merge(df2, df3, how='outer', on=['name','database'])
        df = pd.concat([df, df_m], ignore_index=True)
        df = df[['database', 'name', 'snowflake_row_count', 'sage_row_count']]
        df['delta'] = df['sage_row_count'] - df['snowflake_row_count']
      except IndexError:
        continue
  return df
      
if __name__ == '__main__':
  df = count_rows()
  print(df)