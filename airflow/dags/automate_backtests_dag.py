from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from shared.kafka_producer import send_to_kafka, producer
from scripts.generate_scenes import generate_scenes, process_strategies
from backtest_service.backtest_service import handle_scene

# ... (Your other imports and configurations) ...

with DAG(
    dag_id="backtest_automation_dag",
    schedule_interval="@daily",  # Adjust the schedule as needed
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    def generate_and_send_scenes_task():
        """Generates backtest scenes and sends them to Kafka."""
        process_strategies("strategy_combinations.json")  # Replace with your actual file path

    def run_backtests_task():
        """Consumes scenes from Kafka, runs backtests, and sends results to Kafka."""
        for scene in consume_from_kafka("scenes_topic"):
            handle_scene(scene)

    generate_scenes = PythonOperator(
        task_id="generate_scenes",
        python_callable=generate_and_send_scenes_task,
    )

    run_backtests = PythonOperator(
        task_id="run_backtests",
        python_callable=run_backtests_task,
    )

    generate_scenes >> run_backtests
