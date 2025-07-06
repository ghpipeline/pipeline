from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
from google.cloud import storage, bigquery
from zoneinfo import ZoneInfo


# Mapping folder names to BigQuery dataset and table
FOLDER_TO_BQ = {
    "raw_data": {
        "dataset": "fda_enforcement_data",
        "table": "raw_data"
    },
    # Add more folders if needed
}

# Use Airflow environment variables for flexibility
BQ_PROJECT = os.environ.get("BQ_PROJECT", "globalhealthdatascience")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "fda_enforcement_data")

def load_latest_blob_to_bq(folder="raw_data"):
    if folder not in FOLDER_TO_BQ:
        raise ValueError(f"Folder '{folder}' is not configured.")

    dataset = FOLDER_TO_BQ[folder]["dataset"]
    table = FOLDER_TO_BQ[folder]["table"]
    folder_prefix = f"{folder}/"

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=folder_prefix))

    if not blobs:
        raise FileNotFoundError(f"No files found in '{folder_prefix}'.")

    latest_blob = max(blobs, key=lambda b: b.updated)
    file_uri = f"gs://{BUCKET_NAME}/{latest_blob.name}"

    bq_client = bigquery.Client()
    table_id = f"{BQ_PROJECT}.{dataset}.{table}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = bq_client.load_table_from_uri(file_uri, table_id, job_config=job_config)
    load_job.result()

    print(f"Loaded {latest_blob.name} into {table_id}")

# Default DAG arguments
default_args = {
    #"owner": "airflow",
    #"depends_on_past": False,
    "start_date": datetime(2024, 6, 9, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
    #"retries": 1,
    #"retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="gcs_to_bigquery_load",
    default_args=default_args,
    description="Load latest CSV from GCS into BigQuery",
    schedule_interval=None,
    catchup=False,
    tags=["gcp", "bigquery", "etl"],
) as dag:

    load_task = PythonOperator(
        task_id="load_latest_blob_to_bq",
        python_callable=load_latest_blob_to_bq,
        op_kwargs={"folder": "raw_data"},
    )
