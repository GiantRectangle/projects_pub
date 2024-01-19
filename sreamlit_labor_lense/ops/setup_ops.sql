GRANT CREATE APPLICATION PACKAGE ON ACCOUNT TO ROLE techsolutions;
-- use warehouse DEV_TS_APPLICATION_WAREHOUSE; --couldn't get this to work yet
CREATE APPLICATION PACKAGE labor_lense;
USE APPLICATION PACKAGE labor_lense;
CREATE SCHEMA stage_content;
CREATE OR REPLACE STAGE labor_lense.stage_content.labor_lense_stage
  FILE_FORMAT = (TYPE = 'csv' FIELD_DELIMITER = '|' SKIP_HEADER = 1);
PUT 'file:///C:/Users/SwanS/Sellen Construction Company/Technology Solutions - Documents/Project Truffle Pig/The Labor Lense/sreamlit_labor_lense/manifest.yml' @labor_lense.stage_content.labor_lense_stage overwrite=true auto_compress=false;
PUT 'file:///C:/Users/SwanS/Sellen Construction Company/Technology Solutions - Documents/Project Truffle Pig/The Labor Lense/sreamlit_labor_lense/scripts/setup.sql' @labor_lense.stage_content.labor_lense_stage/scripts overwrite=true auto_compress=false;
PUT 'file:///C:/Users/SwanS/Sellen Construction Company/Technology Solutions - Documents/Project Truffle Pig/The Labor Lense/sreamlit_labor_lense/readme.md' @labor_lense.stage_content.labor_lense_stage overwrite=true auto_compress=false;
PUT 'file:///C:/Users/SwanS/Sellen Construction Company/Technology Solutions - Documents/Project Truffle Pig/The Labor Lense/sreamlit_labor_lense/streamlit/main.py' @labor_lense.stage_content.labor_lense_stage/streamlit overwrite=true auto_compress=false;
CREATE SCHEMA IF NOT EXISTS shared_data;
GRANT REFERENCE_USAGE ON DATABASE prod_publish TO SHARE IN APPLICATION PACKAGE labor_lense;
CREATE VIEW IF NOT EXISTS labor_lense_app_container_view as (
  select
    main_contract
    ,contract
    ,role_l1
    ,role_l2
    ,role_l3
    ,reg_hours
    ,ovt_hours
    ,dt_hours
    ,other_hours
    ,total_hours
    ,job_total_cost
    ,line_total_cost
    ,labor_cost
    ,burden_cost
  from prod_publish.global.labor_lense
);
GRANT USAGE ON SCHEMA shared_data TO SHARE IN APPLICATION PACKAGE labor_lense;
GRANT SELECT ON VIEW labor_lense_app_container_view TO SHARE IN APPLICATION PACKAGE labor_lense;
drop application labor_lense_app;
CREATE APPLICATION labor_lense_app
  FROM APPLICATION PACKAGE labor_lense
  USING '@labor_lense.stage_content.labor_lense_stage';
ALTER APPLICATION PACKAGE labor_lense
  ADD VERSION v1_1 USING '@labor_lense.stage_content.labor_lense_stage';
ALTER APPLICATION PACKAGE labor_lense
  SET DEFAULT RELEASE DIRECTIVE
  VERSION = v1_1
  PATCH = 0;
GRANT APPLICATION ROLE IDENTIFIER('"LABOR_LENSE_APP"."APP_PUBLIC"') TO ROLE IDENTIFIER('"UUR_ADAML"');
GRANT APPLICATION ROLE IDENTIFIER('"LABOR_LENSE_APP"."APP_PUBLIC"') TO ROLE IDENTIFIER('"UUR_RANDYB"');
grant usage on warehouse DEV_TS_DEVELOPER_WAREHOUSE to role uur_adaml;
grant usage on warehouse DEV_TS_DEVELOPER_WAREHOUSE to role uur_randyb;