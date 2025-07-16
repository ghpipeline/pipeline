
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table', schema='world_bank_data') }}

with source_data as (
    select *
    from {{ source('globalhealthdatascience', 'chingchongbingbon') }}
)

select
    country,
    value,
    value * 10 as scaled_value,
from source_data
where value is not null

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
