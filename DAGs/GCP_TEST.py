from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
from google.cloud import storage
import os

def upload_to_gcs():
    # Use PST/PDT for timestamping files
    now_pst = datetime.now(ZoneInfo("America/Los_Angeles"))

    # Unique filename with timestamp
    timestamp_str = now_pst.strftime("%Y%m%d_%H%M%S")
    filename = f"temp_data_{timestamp_str}.csv"

    # Local file path
    local_file_path = f"/opt/airflow/{filename}"

    # Create dummy data
    df = pd.DataFrame({
        "country": ["USA", "Canada", "Mexico"],
        "value": [100, 200, 300]
    })
    df.to_csv(local_file_path, index=False)

    # Upload path in GCS
    bucket_name = "fda_enforcement_data"
    destination_blob_name = f"raw_data/{filename}"

    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)

    print(f"Uploaded {local_file_path} to gs://{bucket_name}/{destination_blob_name}")

# DAG definition
with DAG(
    dag_id="gcs_upload_test_dag",
    start_date=datetime(2024, 6, 9, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
    schedule_interval="0 10 * * *",  # 10:00 AM LOCAL TIME
    catchup=False,
    tags=["test", "gcp"]
) as dag:

    upload_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs
    )
