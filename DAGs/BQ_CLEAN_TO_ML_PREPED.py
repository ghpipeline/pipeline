from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

default_args = {
    #"owner": "airflow",
    #"depends_on_past": False,
    "start_date": datetime(2024, 6, 9, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
    #"retries": 1,
    #"retry_delay": timedelta(minutes=5),
}

BQ_PROJECT = "globalhealthdatascience"
DATASET = "fda_enforcement_data"
CLEANED_TABLE = f"{BQ_PROJECT}.{DATASET}.cleaned_data"
ML_PREPED_TABLE = f"{BQ_PROJECT}.{DATASET}.ml_preped"

ML_PREP_SQL = f"""
CREATE OR REPLACE TABLE `{ML_PREPED_TABLE}` AS
SELECT
    *,
    SAFE_CAST(value AS FLOAT64) AS value_numeric,
    CURRENT_TIMESTAMP() AS prepped_at
FROM `{CLEANED_TABLE}`
WHERE value IS NOT NULL
"""

with DAG(
    dag_id="cleaned_to_ml_preped",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["bigquery", "ml", "prep"],
) as dag:

    prep_for_modeling = BigQueryInsertJobOperator(
        task_id="prep_cleaned_to_ml_ready",
        gcp_conn_id="google_cloud_default",
        configuration={
            "query": {
                "query": ML_PREP_SQL,
                "useLegacySql": False,
            }
        },
    )
