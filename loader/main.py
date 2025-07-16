import datetime
import os
from flask import jsonify, Request
import functions_framework
from google.cloud import storage, bigquery

# Map each subfolder to its BigQuery dataset and table
FOLDER_TO_BQ = {
    "raw_data": {
        "dataset": "fda_enforcement_data",
        "table": "raw_data"
    },
    # Add more folders here as needed
}

BQ_PROJECT = os.environ.get("BQ_PROJECT")
BUCKET_NAME = os.environ.get("BUCKET_NAME") # Single overarching bucket

@functions_framework.http
def daily_gcs_to_bq(request: Request):
    request_json = request.get_json(silent=True)
    folder = request_json.get("folder") if request_json else None

    if not folder:
        return "Missing 'folder' in request body.", 400

    if folder not in FOLDER_TO_BQ:
        return f"Folder '{folder}' is not configured in FOLDER_TO_BQ mapping.", 400

    dataset = FOLDER_TO_BQ[folder]["dataset"]
    table = FOLDER_TO_BQ[folder]["table"]

    # Build folder prefix like 'alpha/2025/07/'
    now = datetime.datetime.utcnow()
    folder_prefix = f"{folder}/{now.year}/{now.month:02d}/"

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=folder_prefix))

    if not blobs:
        return f"No files found in '{folder_prefix}'.", 404

    latest_blob = max(blobs, key=lambda b: b.updated)
    file_uri = f"gs://{BUCKET_NAME}/{latest_blob.name}"

    bq_client = bigquery.Client()
    table_id = f"{BQ_PROJECT}.{dataset}.{table}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = bq_client.load_table_from_uri(
        file_uri,
        table_id,
        job_config=job_config,
    )
    load_job.result()

    return jsonify({
        "message": f"Loaded {latest_blob.name} into {table_id}",
        "bucket": BUCKET_NAME,
        "folder": folder,
        "dataset": dataset,
        "table": table,
        "file": latest_blob.name,
    }), 200
