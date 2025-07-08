from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from google.cloud import storage
import os
import requests
import time

def upload_to_gcs():
    # Use PST/PDT for timestamping files
    now_pst = datetime.now(ZoneInfo("America/Los_Angeles"))

    # Unique filename with timestamp
    timestamp_str = now_pst.strftime("%Y%m%d_%H%M%S")
    filename = f"openfda_data_{timestamp_str}.csv"
    local_file_path = f"/opt/airflow/{filename}"

    # === DATA INGESTION ===
    BASE_URL = "https://api.fda.gov/drug/enforcement.json"
    LIMIT = 100
    SKIP = 0
    ALL_RESULTS = []

    print("Starting paginated data pull from OpenFDA...")

    while True:
        params = {"limit": LIMIT, "skip": SKIP}
        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            print(f"Request failed at skip={SKIP} with status {response.status_code}")
            print(response.text)
            break

        batch = response.json().get("results", [])
        if not batch:
            print("No more data returned. Ending pull.")
            break

        ALL_RESULTS.extend(batch)
        print(f"Pulled {len(batch)} records (Total: {len(ALL_RESULTS)})")
        SKIP += LIMIT
        time.sleep(0.2)

    # Normalize and rename columns for BigQuery compatibility
    df = pd.json_normalize(ALL_RESULTS)
    df.columns = [col.replace('.', '_') for col in df.columns]  # <-- this is the fix
    print(f"Fetched full dataset. Final shape: {df.shape}")

    # Save CSV
    df.to_csv(local_file_path, index=False)

    # Upload to GCS
    bucket_name = "fda_enforcement_data"
    destination_blob_name = f"raw_data/{filename}"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)

    print(f"Uploaded {local_file_path} to gs://{bucket_name}/{destination_blob_name}")

# DAG definition
with DAG(
    dag_id="gcs_upload",
    start_date=datetime(2024, 6, 9, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
    schedule_interval="0 10 * * *",  # 10:00 AM LOCAL TIME
    catchup=False,
    tags=["prod", "gcp", "openfda"]
) as dag:

    upload_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs
    )

