
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table', schema='fda_enforcement_data') }}

with source_data as (
    select *
    from {{ source('globalhealthdatascience', 'ml_predictions') }}
)

select
    true_class,
    pred_class,
    pred_proba,
    run_timestamp
from source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
