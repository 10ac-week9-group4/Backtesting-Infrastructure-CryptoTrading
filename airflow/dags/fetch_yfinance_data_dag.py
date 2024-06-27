import os
import sys
# Add the fetch_data directory to the Python path
sys.path.append('/opt/airflow')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from fetch_data import fetch_and_send_stock_data


with DAG(
    dag_id="fetch_stock_data",
    description="A DAG to fetch and send stock data to Kafka",
    start_date=datetime(2024, 6, 21),
    schedule_interval="@daily",
    catchup=False,
    tags=["atest"],
) as dag:
    fetch_data_task = PythonOperator(
        task_id="fetch_stock_data",
        python_callable=fetch_and_send_stock_data,
        op_args=["AAPL", "5d"],
        # op_args=["AAPL", "2022-06-21", "2024-06-21"]
    )
