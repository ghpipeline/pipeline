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
RAW_TABLE = f"{BQ_PROJECT}.{DATASET}.raw_data"
CLEANED_TABLE = f"{BQ_PROJECT}.{DATASET}.cleaned_data"

# Define your cleaning SQL here
CLEANING_SQL = f"""
CREATE OR REPLACE TABLE `{CLEANED_TABLE}` AS
SELECT
    country,
    SAFE_CAST(value AS INT64) AS value,
    CURRENT_TIMESTAMP() AS cleaned_at
FROM `{RAW_TABLE}`
WHERE SAFE_CAST(value AS INT64) IS NOT NULL
"""

with DAG(
    dag_id="clean_raw_data_to_cleaned_data",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["bigquery", "cleaning"],
) as dag:

    clean_data = BigQueryInsertJobOperator(
        task_id="clean_raw_to_cleaned",
        configuration={
            "query": {
                "query": CLEANING_SQL,
                "useLegacySql": False,
            }
        },
    )
