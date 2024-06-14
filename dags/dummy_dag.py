from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'nathanael',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=2),
}

with DAG (
    dag_id = 'dummy_dag',
    default_args = default_args,
    description = 'This is a dummy DAG',
    start_date = datetime(2024, 6, 13),
    schedule_interval = '@daily',
) as dag:
    task = BashOperator(
        task_id = 'dummy_task',
        bash_command = 'echo "Hello World"',
    )

