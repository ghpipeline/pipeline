from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def my_task():
    print("Hello from DAG!")

with DAG(
    dag_id="my_example_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["test"]
) as dag:
    task = PythonOperator(
        task_id="say_hello",
        python_callable=my_task,
    )

