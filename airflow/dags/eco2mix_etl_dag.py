from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.decorators import dag, task
from src.main.update_data import get_last_date, fetch_data, repair_data, clean_data, del_excel_files
from src.main.insert_data import connect, insert_data
import logging
from kafka_utils import send_kafka_message, consume_kafka_message
import pandas as pd


logger = logging.getLogger("airflow.task")

@task
def extract_data(**kwargs):
    try :
        day, month, year = get_last_date()
        fetch_data(day, month, year)
    except Exception as e:
        logger.error(f"An error occurred while extracting the data: {e}")
    else :
        logger.info("Extracted data")
        send_kafka_message('data_extracted', {'day': day, 'month': month, 'year': year})
        # kwargs['ti'].xcom_push(key='date_info', value={'day': day, 'month': month, 'year': year})

@task
def transform_data(**kwargs):
    # date_info = kwargs['ti'].xcom_pull(key='date_info', task_ids='extract_data')
    date_info = consume_kafka_message('data_extracted')
    day, month, year = date_info['day'], date_info['month'], date_info['year']
    try :
        df = repair_data(day, month, year)
        df = clean_data(df)
        del_excel_files(day, month, year)
    except Exception as e:
        logger.error(f"An error occurred while transforming the data: {e}")
    else :
        logger.info("Transformed data")
        # kwargs['ti'].xcom_push(key='cleaned_df', value=df)
        send_kafka_message('data_transformed', {'dataframe': df.to_json()})

@task
def load_data(**kwargs):
    # df = kwargs['ti'].xcom_pull(key='cleaned_df', task_ids='transform_data')
    transformed_data = consume_kafka_message('data_transformed')
    df = pd.read_json(transformed_data['dataframe'])
    try:
        engine = connect()
        insert_data(df)
    except Exception as e:
        logger.error(e)
    else:
        logger.info("Data loaded successfully")
    finally:
        if engine:
            engine.dispose()
            logger.info("Connection closed")

@dag(
    default_args={
        'owner': 'nathanael',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(seconds=30),
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
