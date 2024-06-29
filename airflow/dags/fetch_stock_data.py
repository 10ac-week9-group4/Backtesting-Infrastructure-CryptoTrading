import os
import sys
# Add the directory containing save_asset_and_stock.py to the Python path
sys.path.append('/opt/airflow')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from save_asset_and_stock import create_or_update_assets_send_to_kafka, consume_assets_and_fetch_data, fetch_top_20_assets

with DAG(
  dag_id="fetch_stock_data",
  description="A DAG to process assets and stock data, then send to Kafka",
  start_date=datetime(2024, 6, 21),
  schedule_interval="@daily",
  catchup=False,
  tags=["finance", "assets", "kafka"],
) as dag:
  fetch_top_20_assets_task = PythonOperator(
    task_id="fetch_top_20_assets",
    python_callable=fetch_top_20_assets,
  )

  create_or_update_assets_send_to_kafka_task = PythonOperator(
    task_id="create_or_update_assets_send_to_kafka",
    python_callable=create_or_update_assets_send_to_kafka,
    op_args=[fetch_top_20_assets_task.output],  # Assuming this function can handle the output directly
  )

  consume_assets_and_fetch_data_task = PythonOperator(
    task_id="consume_assets_and_fetch_data",
    python_callable=consume_assets_and_fetch_data,
  )

  fetch_top_20_assets_task >> create_or_update_assets_send_to_kafka_task >> consume_assets_and_fetch_data_task