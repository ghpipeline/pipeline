import datetime
import os
from flask import jsonify, Request
import functions_framework
from google.cloud import storage, bigquery

# Map each bucket to its BigQuery dataset and table
BUCKET_TO_BQ = {
    "bucket-alpha": {
        "dataset": "dataset_alpha",
        "table": "data_alpha"
    },
    "bucket-beta": {
        "dataset": "dataset_beta",
        "table": "data_beta"
    },
    # Add more buckets here as needed
}

BQ_PROJECT = os.environ.get("BQ_PROJECT")  # Set this in your Cloud Function environment variables

@functions_framework.http
def daily_gcs_to_bq(request: Request):
    request_json = request.get_json(silent=True)
    bucket_name = None

    if request_json and "bucket" in request_json:
        bucket_name = request_json["bucket"]
    else:
        bucket_name = os.environ.get("BUCKET_NAME")

    if not bucket_name:
        return "Missing 'bucket' in request body or BUCKET_NAME environment variable.", 400

    if bucket_name not in BUCKET_TO_BQ:
        return f"Bucket '{bucket_name}' is not configured in BUCKET_TO_BQ mapping.", 400

    dataset = BUCKET_TO_BQ[bucket_name]["dataset"]
    table = BUCKET_TO_BQ[bucket_name]["table"]

    # Build folder prefix based on current year and month (UTC)
    now = datetime.datetime.utcnow()
    folder_prefix = f"{now.year}/{now.month:02d}/"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = list(bucket.list_blobs(prefix=folder_prefix))

    if not blobs:
        return f"No files found in bucket '{bucket_name}' with prefix '{folder_prefix}'.", 404

    # Find the most recently updated blob
    latest_blob = max(blobs, key=lambda b: b.updated)

    file_uri = f"gs://{bucket_name}/{latest_blob.name}"

    bigquery_client = bigquery.Client()
    table_id = f"{BQ_PROJECT}.{dataset}.{table}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = bigquery_client.load_table_from_uri(
        file_uri,
        table_id,
        job_config=job_config,
    )
    load_job.result()  # Wait for job to complete

    return jsonify({
        "message": f"Successfully loaded {latest_blob.name} into {table_id}",
        "bucket": bucket_name,
        "dataset": dataset,
        "table": table,
        "file": latest_blob.name,
    }), 200
