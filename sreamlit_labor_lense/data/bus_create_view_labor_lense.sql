--liquibase formatted sql
--changeset ${ENV}:1 runOnChange:true labels:04_publish/ddl/global_${ENV}-label context:bus_create_view_labor_lense_${ENV}.sql

/*###############################################################
title: create labor_rates view
usage: business view of labor burden analysis
author: Swan S.
description: 
system: snowflake
################################################################*/
create or replace view ${ENV}_publish.global.labor_lense as (
    with cte_ld as (
        select 
            job_number
            ,craft
            ,class
            ,sum(case when udearncat = 'RT' then hours else 0 end) reg_hours
            ,sum(case when udearncat = 'OT' then hours else 0 end) ovt_hours
            ,sum(case when udearncat = 'DT' then hours else 0 end) dt_hours
            ,sum(case when udearncat = 'Other' then hours else 0 end) other_hours
            ,sum(case when udearncat in ('RT', 'OT', 'DT', 'Other') then hours else 0 end) total_hours
        from   ${ENV}_publish.vista.src_vista_pr_join_recipe
        group by job_number, craft, class )
    ,cte_burd as (
        select 
            split_part(contract, '.', 1) main_contract
            ,contract
            ,craft
            ,class
            ,sum(actualcost) total_cost
            ,sum(case when costtype = 1 then actualcost else 0 end) labor_cost
            ,sum(case when costtype = 2 then actualcost else 0 end) burden_cost
            ,div0(burden_cost, labor_cost) burden_prct
            ,min(month) start_month
            ,max(month) end_month
            ,datediff(month, start_month, end_month) duration_months
        from ${ENV}_publish.vista.src_actual_cost_trending act
        group by contract, craft, class )
select 
    main_contract
    ,contract
    ,cb.craft
    ,cb.class
    ,role_l1
    ,role_l2
    ,role_l3
    ,job_title
    ,job_class
    ,job_trade
    ,reg_hours
    ,ovt_hours
    ,dt_hours
    ,other_hours
    ,total_hours
    ,sum(total_cost) over (partition by contract) job_total_cost
    ,total_cost line_total_cost
    ,labor_cost
    ,div0(labor_cost, total_hours) price_per_hour
    ,burden_cost
    ,start_month
    ,end_month
    ,duration_months
from  (cte_burd cb
left outer join ${ENV}_publish.vista.src_vista_roles_keys rk
on (cb.craft = rk.craft) and (cb.class = rk.class))
left outer join cte_ld ld
on (cb.craft = ld.craft) and (cb.class = ld.class) and (cb.contract = ld.job_number) 
)
;

-- rollback