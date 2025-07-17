{{ config(materialized='table', schema='fda_enforcement_data') }}

with source_data as (

    select
        *,
        SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)) AS recall_initiation_dt,
        SAFE.PARSE_DATE('%Y%m%d', CAST(center_classification_date AS STRING)) AS center_classification_dt,
        SAFE.PARSE_DATE('%Y%m%d', CAST(termination_date AS STRING)) AS termination_dt,
        SAFE.PARSE_DATE('%Y%m%d', CAST(report_date AS STRING)) AS report_dt,
        DATE_DIFF(
            SAFE.PARSE_DATE('%Y%m%d', CAST(termination_date AS STRING)),
            SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)),
            DAY
        ) AS recall_duration_days,
        DATE_DIFF(
            SAFE.PARSE_DATE('%Y%m%d', CAST(center_classification_date AS STRING)),
            SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)),
            DAY
        ) AS time_to_classification_days,
        DATE_DIFF(
            SAFE.PARSE_DATE('%Y%m%d', CAST(report_date AS STRING)),
            SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)),
            DAY
        ) AS report_lag_days,
        EXTRACT(YEAR FROM SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING))) AS initiation_year,
        EXTRACT(MONTH FROM SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING))) AS initiation_month,
        EXTRACT(DAYOFWEEK FROM SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING))) AS initiation_dayofweek,
        LENGTH(cleaned_description) AS desc_length,
        ARRAY_LENGTH(SPLIT(cleaned_description, ' ')) AS desc_word_count,
        REGEXP_CONTAINS(cleaned_description, r'injection') AS has_injection,
        REGEXP_CONTAINS(cleaned_description, r'tablet') AS has_tablet,
        REGEXP_CONTAINS(cleaned_description, r'capsule') AS has_capsule,
        REGEXP_CONTAINS(cleaned_description, r'spray') AS has_spray,
        REGEXP_CONTAINS(LOWER(IFNULL(product_quantity, '')), r'single dose|unit dose|1 count') AS has_single_unit,
        REGEXP_CONTAINS(LOWER(IFNULL(product_quantity, '')), r'1000 count|bulk|100 count|box') AS has_bulk,
        REGEXP_CONTAINS(LOWER(IFNULL(product_quantity, '')), r'box') AS has_box,
        LENGTH(IFNULL(product_quantity, '')) AS quantity_length,
        ARRAY_LENGTH(SPLIT(IFNULL(product_quantity, ''), ' ')) AS quantity_word_count,
        IF(UPPER(country) = 'UNITED STATES', 1, 0) AS is_us,
        IF(UPPER(country) != 'UNITED STATES', 1, 0) AS is_foreign,
        IF(UPPER(state) = 'CA', 1, 0) AS is_ca_state,
        REGEXP_CONTAINS(reason_for_recall, r'(?i)contaminat') AS mention_contamination,
        REGEXP_CONTAINS(reason_for_recall, r'(?i)label|mislab|incorrect') AS mention_label_error,
        REGEXP_CONTAINS(reason_for_recall, r'(?i)potency|strength') AS mention_potency,
        REGEXP_CONTAINS(reason_for_recall, r'(?i)steril') AS mention_sterility,
        CURRENT_TIMESTAMP() AS prepped_at
    from {{ source('globalhealthdatascience', 'cleaned_data') }}
    where cleaned_description is not null

)

select *
from source_data
