from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os

# Define the path to your Python script
script_path = "/path/to/your/main.py"

def run_backtest():
  # Ensure the Python environment is correctly set up (e.g., activate virtualenv if needed)
  os.system(f"python {script_path}")

# Define default arguments for the DAG
default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': datetime(2023, 1, 1),
  'email_on_failure': False,
  'email_on_retry': False,
  'retries': 1,
  'retry_delay': timedelta(minutes=5),
}

# Define the DAG, its schedule, and catchup behavior
dag = DAG(
  'backtest_automation',
  default_args=default_args,
  description='Automate backtesting of trading strategies',
  schedule_interval=timedelta(days=1),
  catchup=False,
)

# Define the task to run backtest
run_backtest_task = PythonOperator(
  task_id='run_backtest',
  python_callable=run_backtest,
  dag=dag,
)

# Set the task sequence
run_backtest_task