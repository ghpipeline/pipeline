from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from google.cloud import storage
import os

def upload_to_gcs():
    # Timezone-aware timestamp in PST
    now_pst = datetime.now(ZoneInfo("America/Los_Angeles"))
    
    # Create folder structure based on date
    folder_path = now_pst.strftime("%Y/%m/%d")
    
    # Create a unique filename using timestamp
    timestamp_str = now_pst.strftime("%Y%m%d_%H%M%S")
    filename = f"temp_data_{timestamp_str}.csv"
    
    # Full local path to save CSV
    local_file_path = f"/opt/airflow/{filename}"

    # Create dummy data
    df = pd.DataFrame({
        "country": ["USA", "Canada", "Mexico"],
        "value": [100, 200, 300]
    })
    df.to_csv(local_file_path, index=False)

    # GCS upload target path
    bucket_name = "world_bank_raw"
    destination_blob_name = f"test_upload/{folder_path}/{filename}"

    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)

    print(f"Uploaded {local_file_path} to gs://{bucket_name}/{destination_blob_name}")

with DAG(
    dag_id="gcs_upload_test_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 10 * * *",
    catchup=False,
    tags=["test", "gcp"]
) as dag:

    upload_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs
    )
