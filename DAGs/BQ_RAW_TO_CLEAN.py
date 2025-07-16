from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from google.cloud import bigquery
import pandas as pd
import re
from zoneinfo import ZoneInfo

BQ_PROJECT = "globalhealthdatascience"
DATASET = "fda_enforcement_data"
RAW_TABLE = f"{BQ_PROJECT}.{DATASET}.raw_data"
CLEANED_TABLE = f"{BQ_PROJECT}.{DATASET}.cleaned_data"

def clean_bq_data():
    # === Step 1: Read raw data from BQ ===
    client = bigquery.Client()
    query = f"SELECT * FROM `{RAW_TABLE}`"
    df = client.query(query).to_dataframe()
    print(f"Fetched {df.shape} rows from raw_data.")

    # === Step 2: Drop Irrelevant Columns ===
    drop_cols = [
        "address_2", "more_code_info", "openfda_upc", "openfda_nui",
        "openfda_pharm_class_moa", "openfda_pharm_class_epc", "openfda_pharm_class_cs",
        "openfda_original_packager_product_ndc", "openfda_pharm_class_pe",
        "event_id", "recall_number", "code_info", "postal_code", "application_number",
        "openfda_is_original_packager", "openfda_rxcui", "openfda_application_number",
        "openfda_substance_name", "openfda_unii", "openfda_route", "openfda_package_ndc",
        "openfda_spl_set_id", "openfda_spl_id", "openfda_product_type", "openfda_product_ndc",
        "openfda_manufacturer_name", "openfda_generic_name", "openfda_brand_name", "product_type"
    ]
    existing_to_drop = [col for col in drop_cols if col in df.columns]
    df.drop(columns=existing_to_drop, inplace=True)
    print(f"Dropped {len(existing_to_drop)} columns. Remaining: {df.shape}")

    # === Step 3: Create Target Variable ===
    df["is_class_1"] = df["classification"].apply(lambda x: 1 if str(x).strip().upper() == "CLASS I" else 0)

    # === Step 4: Clean product_description ===
    def clean_text(text):
        if pd.isna(text):
            return ""
        text = text.lower()
        text = re.sub(r'ndc\s*\d+', ' ', text)
        text = re.sub(r'upc\s*\d+', ' ', text)
        text = re.sub(r'\b\d{5}\b', ' ', text)
        text = re.sub(r'\b(rx|only|llc|inc|code|vial|bottle|count|ml|mg|mcg|fl oz|oz|tablet|capsule|usp)\b', ' ', text)
        text = re.sub(r'[^a-z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    df["cleaned_description"] = df["product_description"].apply(clean_text)

    # === Step 5: Write cleaned data back to BigQuery ===
    df["cleaned_at"] = pd.Timestamp.now(tz="UTC")
    df.to_gbq(
        destination_table=f"{DATASET}.cleaned_data",
        project_id=BQ_PROJECT,
        if_exists="replace"  # or "append" if you prefer
    )

    print(f"Uploaded cleaned data to {CLEANED_TABLE}")

# Define DAG
with DAG(
    dag_id="bq_clean_raw_to_cleaned_data",
    start_date=datetime(2024, 6, 9, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
    schedule_interval="@daily",
    catchup=False,
    tags=["bq", "cleaning", "pandas"]
) as dag:

    clean_task = PythonOperator(
        task_id="clean_raw_to_cleaned",
        python_callable=clean_bq_data
    )
