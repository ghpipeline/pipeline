from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

default_args = {
    "start_date": datetime(2024, 6, 9, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
}

BQ_PROJECT = "globalhealthdatascience"
DATASET = "fda_enforcement_data"
CLEANED_TABLE = f"{BQ_PROJECT}.{DATASET}.cleaned_data"
ML_PREPED_TABLE = f"{BQ_PROJECT}.{DATASET}.ml_preped"

# BigQuery SQL logic with preprocessing features
ML_PREP_SQL = f"""
CREATE OR REPLACE TABLE `{ML_PREPED_TABLE}` AS
SELECT
    *,
    SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)) AS recall_initiation_dt,
    SAFE.PARSE_DATE('%Y%m%d', CAST(center_classification_date AS STRING)) AS center_classification_dt,
    SAFE.PARSE_DATE('%Y%m%d', CAST(termination_date AS STRING)) AS termination_dt,
    SAFE.PARSE_DATE('%Y%m%d', CAST(report_date AS STRING)) AS report_dt,
    DATE_DIFF(SAFE.PARSE_DATE('%Y%m%d', CAST(termination_date AS STRING)), SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)), DAY) AS recall_duration_days,
    DATE_DIFF(SAFE.PARSE_DATE('%Y%m%d', CAST(center_classification_date AS STRING)), SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)), DAY) AS time_to_classification_days,
    DATE_DIFF(SAFE.PARSE_DATE('%Y%m%d', CAST(report_date AS STRING)), SAFE.PARSE_DATE('%Y%m%d', CAST(recall_initiation_date AS STRING)), DAY) AS report_lag_days,
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
FROM `{CLEANED_TABLE}`
WHERE cleaned_description IS NOT NULL
"""


with DAG(
    dag_id="cleaned_to_ml_preped",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["bigquery", "ml", "prep"],
) as dag:

    prep_for_modeling = BigQueryInsertJobOperator(
        task_id="cleaned_to_ml_ready",
        gcp_conn_id="google_cloud_default",
        configuration={
            "query": {
                "query": ML_PREP_SQL,
                "useLegacySql": False,
            }
        },
    )
