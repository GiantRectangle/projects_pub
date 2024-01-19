import pyodbc
import pandas as pd
import json

# set credentials
with open(r'C:\_scripts\secrets.json') as f:
    scr = json.load(f)
username = scr['sage']['username']
password = scr['sage']['password']
server = 'estima_test'

conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'  
    f'SERVER={server};'
    f'DATABASE=Live_Database;'
    f'UID={username};'
    f'PWD={password};'
    'ENCRYPT=no;'  # this line has to be added in order to get the latest driver to work. also it has to be set to no, because evidently that's what it is on the server side
    'Trusted_Connection=yes;'  # commenting out this line makes the whole thing stop working. the hope was to start forcing folks to enter credentials
)
cursor = conn.cursor()

# don't do any of this yet!!!!
query = f'''
    something something StoredProcedure [dbo].[est_Estimate_Copy]
    actually, probably StoredProcedure [dbo].[est_Estimate_Insert]
    something something StoredProcedure [dbo].[est_Assembly_Select]
    something something StoredProcedure [dbo].[est_Item_BulkInsert]
'''

cursor.execute(query) # this is what we'll need to actually exectute the sp's

df = pd.read_sql_query(query ,conn, chunksize=1_000_000) # this will be usefull at least for exploring and debugging while we're building it