--liquibase formatted sql
--changeset ${ENV}:1 runOnChange:true labels:04_publish/ddl/vista_${ENV}-label context:bus_create_dyn_table_src_vista_pr_join_recipe_${ENV}.sql

/*###############################################################
# title: create dynamic table src vista pr join recipe
# usage: vista business logic unit for analysis as required
# author: Swan Sodja
# description: basis for various payroll reports including labor detail and labor summary
# system: snowflake
################################################################*/
create or replace dynamic table ${ENV}_publish.vista.src_vista_pr_join_recipe 
   lag = '1 hour' 
   initialize = on_create 
   warehouse = ${ENV}_ts_elt_warehouse
as 
    select 
        trim(prth.job, ' .') job_number
        ,prth.employee
        ,prehfullname.fullname full_name
        ,prth.earncode
        ,prth.hours
        ,prth.amt prth_amt
        ,jcjm.description job_name
        ,trim(prth.phase, ' .') phase_code
        ,jcjm.job
        ,jcjm.jobstatus -- active jobs = 1
        ,prth.prco
        ,jcjp.description phase_description
        ,prehfullname.sortname
        ,to_date(prth.prenddate) pr_end_date
        ,to_date(prth.postdate) post_date
        ,trim(prth.craft) craft
        ,trim(prth.class) class
        ,trim(prth.craft) || ' - ' || trim(prth.class) cc_key
        ,prta.amt prta_amt
        ,ifnull(prec_prta.udearncat,'') prta_udearncat
        ,ifnull(prec.jccosttype,prec_prta.jccosttype) cost_type 
        ,ifnull(prec.udearncat,'') udearncat 
    from   (((((${ENV}_gold.vista.prth prth 
    left outer join ${ENV}_gold.vista.prehfullname prehfullname 
    on (prth.prco=prehfullname.prco) and (prth.employee=prehfullname.employee)) 
    left outer join ${ENV}_gold.vista.prec prec 
    on (prth.prco=prec.prco) and (prth.earncode=prec.earncode)) 
    left outer join ${ENV}_gold.vista.jcjm jcjm 
    on (prth.jcco=jcjm.jcco) and (prth.job=jcjm.job)) 
    left outer join ${ENV}_gold.vista.jcjp jcjp 
    on (((prth.jcco=jcjp.jcco) and (prth.job=jcjp.job)) and (prth.phasegroup=jcjp.phasegroup)) and (prth.phase=jcjp.phase)) 
    left outer join ${ENV}_gold.vista.prta prta 
    on (((((prth.prco=prta.prco) and (prth.prgroup=prta.prgroup)) and (prth.prenddate=prta.prenddate)) and (prth.employee=prta.employee)) and (prth.payseq=prta.payseq)) and (prth.postseq=prta.postseq)) 
    left outer join ${ENV}_gold.vista.prec prec_prta 
    on (prta.prco=prec_prta.prco) and (prta.earncode=prec_prta.earncode)
    where  prth.prco=1 
    and (prth.prenddate>={ts '1950-01-01 00:00:00'} and prth.prenddate<{ts '2051-01-01 00:00:00'}) 
    and (prth.craft>=' ' and prth.craft<='zzzzzzzzzz') ;

-- rollback