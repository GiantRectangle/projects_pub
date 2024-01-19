-- fundamental setup
CREATE APPLICATION ROLE app_public;
CREATE SCHEMA IF NOT EXISTS core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_public;

-- add a sproc
CREATE OR REPLACE PROCEDURE CORE.HELLO()
  RETURNS STRING
  LANGUAGE SQL
  EXECUTE AS OWNER
  AS
  BEGIN
    RETURN 'Hello Snowflake!';
  END;
GRANT USAGE ON PROCEDURE core.hello() TO APPLICATION ROLE app_public;

-- add a spot for data to be accessed by the app
CREATE OR ALTER VERSIONED SCHEMA code_schema;
GRANT USAGE ON SCHEMA code_schema TO APPLICATION ROLE app_public;
CREATE VIEW IF NOT EXISTS code_schema.labor_lense_app_view
  AS SELECT *
  FROM shared_data.labor_lense_app_container_view;
GRANT SELECT ON VIEW code_schema.labor_lense_app_view TO APPLICATION ROLE app_public;

-- add a streamlit app
CREATE STREAMLIT code_schema.labor_lense_streamlit
  FROM '/streamlit'
  MAIN_FILE = '/main.py'
;
GRANT USAGE ON STREAMLIT code_schema.labor_lense_streamlit TO APPLICATION ROLE app_public;