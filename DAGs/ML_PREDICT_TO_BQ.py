from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from google.cloud import bigquery
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

MODEL_PATH = "/models/ml_models/xgb_model.joblib"
SCALER_PATH = "/models/ml_scalers/scaler.joblib"
SELECTOR_PATH = "/models/ml_scalers/feature_selector.joblib"
FEATURE_NAMES_PATH = "/models/ml_scalers/feature_names.joblib"

PROJECT_ID = "globalhealthdatascience"
DATASET = "fda_enforcement_data"
SOURCE_TABLE = "ml_preped"
DEST_TABLE = "ml_predictions"

def predict_and_write():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{SOURCE_TABLE}`"
    df = client.query(query).to_dataframe()

    # Load saved model artifacts
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    selector = joblib.load(SELECTOR_PATH)
    feature_names = joblib.load(FEATURE_NAMES_PATH)

    y_true = df["is_class_1"]
    df = df.drop(columns=["is_class_1"])

    # === Recreate all feature engineering from training ===
    categorical_cols = ["status", "voluntary_mandated", "initial_firm_notification", "country"]
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Add any missing dummy columns
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns to match training
    df = df[feature_names]

    # Drop any rows with NaNs
    df.dropna(inplace=True)

    # Align target variable length after dropping
    y_true = y_true.loc[df.index]

    # Now apply scaler to entire DataFrame as in training
    X_scaled = scaler.transform(df)

    # Feature selection
    X_selected = selector.transform(X_scaled)

    # Predict
    y_proba = model.predict_proba(X_selected)[:, 1]
    y_pred = model.predict(X_selected)

    results_df = pd.DataFrame({
        "true_class": y_true,
        "pred_class": y_pred,
        "pred_proba": y_proba,
        "run_timestamp": datetime.utcnow().isoformat()
    })

    results_df.to_gbq(
        destination_table=f"{DATASET}.{DEST_TABLE}",
        project_id=PROJECT_ID,
        if_exists="replace"
    )
    
with DAG(
    dag_id="ml_prediction_pipeline",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=["ml", "xgboost", "prediction"],
) as dag:

    predict_task = PythonOperator(
        task_id="predict_and_write_to_bigquery",
        python_callable=predict_and_write
    )
