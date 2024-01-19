--liquibase formatted sql
--changeset ${ENV}:1 runOnChange:true labels:04_publish/ddl/vista_${ENV}-label context:bus_create_dyn_table_src_src_vista_roles_keys_${ENV}.sql

/*###############################################################
# title: create dynamic table src vista roles keys
# usage: vista business logic unit regarding employee roles for analysis as required
# author: Swan Sodja
# description: it's the decoder ring for roles
# system: snowflake
-- ################################################################*/
create or replace dynamic table ${ENV}_publish.vista.src_vista_roles_keys (
    craft
    ,class
    ,cc_key
    ,job_title
    ,job_class
    ,job_trade
    ,role_l1
    ,role_l2
    ,role_l3
)
   lag = '1 hour' 
   initialize = on_create 
   warehouse = ${ENV}_ts_elt_warehouse
as 
    with cc_k as (
        select
            distinct
            trim(prcc.craft) craft
            ,trim(prcc.class) class
            ,trim(prcc.craft) || ' - ' || trim(prcc.class) cc_key
            ,mode(description) job_title
            ,mode(udkdsclassdisplay) job_class
            ,mode(udpwtrade) job_trade
            ,case
                when (class in ('201A', '201L', '216', '200P', '201LP', '201', '203', '217', '213', '200GFM', '200GFMP', '218', '212', '214', '220', '211', '200', '202', '215')) or (job_title like '%CARPENTER JOURNEYMAN%') then 'Carpenter'
                when (class in ('303', '313', '314', '316M', '312A', '300p', '316', '302', '312AM', '301', '314M', '312', '315M', '300', '313M', '304', '311', '311M', '312M', '315', '301P')) or (class = '902' and craft = '30') or (class = '901' and craft = '30') then 'Cement Mason'
                when (class in ('400', '402', '410', '401O', '415', '416', '412', '413', '400O', '414A', '403', '411', '401', '414')) or (class = '902' and craft = '40') then 'Ironworker'
                when (class in ('502', '503LN', '517', '501', '519N', '511', '514N', '511M', '502N', '503', '518N', '500GFM', '500', '513', '514', '519', '500GFMP', '511N', '512M', '503N', '513AN', '513N', '513A', '515N', '503L', '515', '512N', '501P', '514M', '500N', '518', '521N', '501N', '505', '500GFN', '520N', '513M', '516N', '500P', '520', '512', '515M', '517N', '521', '516', '504', '513AM')) and (craft != '99') then 'Laborer'
                when (class in ('614', '602', '603', '611', '606', '615', '600', '903A', '604', '612', '616', '601', '600GFM', '618', '613', '605', '606SP', '601FMP', '617')) or (class in ('902A', '902', '903') and craft = '60') then 'Operator'
                when ((craft = '99') and (class in ('513M', '514M', '999D', '515M', '999', '1', '513AM', '999A', '909'))) or (craft in ('92', '98', '98A', '999', '999A', '999D')) then 'Undefined'
                when (class like'9%') and not ((class = '902' and craft in ('30', '40', '60')) or (class = '901' and craft = '30') or (craft in ('92', '98', '98A', '999', '999A', '999D'))) then 'Supervision'
                else ''
                end role_l2
            ,case
                when role_l2 in ('Carpenter', 'Cement Mason', 'Ironworker', 'Laborer', 'Operator') then 'Craft'
                when role_l2 = 'Undefined' then 'Undefined'
                else 'Supervision'
                end role_l1
            ,case
                when (role_l1 = 'Craft') and (class in ('313', '614', '517', '314', '316M', '415', '519N', '611', '312A', '511', '511M', '514N', '316', '411', '216', '414', '312AM', '518N', '615', '513', '314M', '416', '312', '514', '412', '519', '511N', '512M', '217', '315M', '513AN', '213', '513A', '513N', '515N', '515', '612', '512N', '616', '514M', '313M', '618', '218', '518', '521N', '311', '311M', '212', '214', '312M', '413', '613', '520N', '513M', '516N', '211', '520', '410', '315', '512', '215', '515M', '517N', '521', '414A', '516', '513AM', '617')) then 'Apprentice'
                when (role_l1 = 'Craft') and (class in ('201A', '303', '502', '503LN', '602', '603', '201L', '502N', '503', '606', '201LP', '600', '201', '203', '503N', '604', '503L', '601', '304', '403', '505', '605', '402', '606SP', '202', '504')) or (job_title like '%JOURNEYMAN%') then 'Journeyman'
                when ((role_l1 = 'Craft') and (class in ('400', '501', '300p', '400O', '401', '302', '200P', '500GFM', '301', '500', '401O', '500GFMP', '600GFM', '200GFM', '501P', '300', '500N', '200GFMP', '501N', '500GFN', '220', '500P', '900', '301P', '200', '601FMP'))) or ((craft = '99') and (class = '900')) then 'Foreman'
                when (craft = '99') and (class in ('973', '975', '974', '974B'))  then 'Accounting'
                when (craft = '99') and (class in ('972', '971', '972A', '970'))  then 'Admin'
                when (class = '901') or ((craft = '60') and (class in ('903', '903A'))) or ((craft = '99') and (class = '976')) then 'Assistant Superintendent'
                when (class in ('997A', '990', '995', '998', '991', '992', '997', '994', '993', '992A')) or ((craft = '20') and (class = '964')) then 'Engineer'
                when class = '980' then 'Project Manager'
                when class = '911' then 'Senior Leadership'
                when class in ('986', '985') then 'Quality Control'
                when (class in ('960', '960B', '961', '960A', '901A', '963', '962', '963P')) or ((craft = '99') and (class = '964')) then 'Safety'
                when (class in ('991A', '902A', '902', '904', '905', '940')) or ((craft != '60') and (class = '903')) then 'Superintendent'
                when class in ('999B', '999C') then 'Sustainability'
                when class in ('996', '930', '931') then 'VDC'
                when (class in ('908', '974A', '907', '974AB', '910', '906', '900A')) or ((craft = '50') and (class = '900')) then 'Warehouse'
                when role_l1 = 'Undefined' then 'Undefined'
                else ''
                end role_l3
        from ${ENV}_gold.vista.prcc prcc
        group by class, craft   )
    select
        mode(craft) craft
        ,mode(class) class
        ,cc_key
        ,mode(job_title) job_title
        ,mode(job_class) job_class
        ,mode(job_trade) job_trade
        ,mode(role_l1) role_l1
        ,mode(role_l2) role_l2
        ,mode(role_l3) role_l3
    from cc_k
    group by cc_key
    
    ;

-- rollback
