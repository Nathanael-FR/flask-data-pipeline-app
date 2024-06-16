from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.decorators import dag, task
from dags.src.main.update_data import get_last_date, fetch_data, repair_data, clean_data, del_excel_files, connect, insert_data
import logging

@task
def extract_data(**kwargs):
    day, month, year = get_last_date()
    fetch_data(day, month, year)
    # Pass day, month, year to the next task using XCom
    logging.info("Extracted data")
    kwargs['ti'].xcom_push(key='date_info', value={'day': day, 'month': month, 'year': year})

@task
def transform_data(**kwargs):
    date_info = kwargs['ti'].xcom_pull(key='date_info', task_ids='extract_data')
    day, month, year = date_info['day'], date_info['month'], date_info['year']
    df = repair_data(day, month, year)
    df = clean_data(df)
    del_excel_files(day, month, year)
    # Push the cleaned dataframe to XCom
    logging.info("Transformed data")
    kwargs['ti'].xcom_push(key='cleaned_df', value=df)

@task
def load_data(**kwargs):
    df = kwargs['ti'].xcom_pull(key='cleaned_df', task_ids='transform_data')
    try:
        engine = connect()
        insert_data(df)
    except Exception as e:
        logging.error(e)
    else:
        logging.info("Data loaded successfully")
    finally:
        if engine:
            engine.dispose()
            logging.info("Connection closed")

@dag(
    default_args={
        'owner': 'nathanael',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    },
    description='ETL process for eco2mix data',
    start_date=datetime(2021, 1, 1),
    schedule_interval='@daily',
    catchup=False,
)
def eco2mix_etl_dag():
    extract_task = extract_data()
    transform_task = transform_data()
    load_task = load_data()
    
    extract_task >> transform_task >> load_task

dag = eco2mix_etl_dag()
