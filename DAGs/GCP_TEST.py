from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from google.cloud import storage
import os

def upload_to_gcs():
    # Create dummy data
    df = pd.DataFrame({
        "country": ["USA", "Canada", "Mexico"],
        "value": [100, 200, 300]
    })

    # Write to CSV
    local_file_path = "/opt/airflow/temp_data.csv"
    df.to_csv(local_file_path, index=False)

    # GCS upload
    bucket_name = "world_bank_raw"
    destination_blob_name = "test_upload/temp_data.csv"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)

    print(f"Uploaded {local_file_path} to {bucket_name}/{destination_blob_name}")

with DAG(
    dag_id="gcs_upload_test_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["test", "gcp"]
) as dag:

    upload_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs
    )

