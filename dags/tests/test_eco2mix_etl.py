import pytest
from airflow import DAG
from airflow.models import DagBag
from dags.eco2mix_etl_dag import dag, extract_data, transform_data, load_data
import pandas as pd

def test_dag_structure():
    assert isinstance(dag, DAG)
    assert len(dag.tasks) == 3
    assert set([task.task_id for task in dag.tasks]) == {"extract_data", "transform_data", "load_data"}

@pytest.fixture
def context(mocker):
    mocker.patch('dags.eco2mix_etl_dag.get_last_date', return_value=(1, 1, 2021))
    mocker.patch('dags.eco2mix_etl_dag.fetch_data')
    mocker.patch('dags.eco2mix_etl_dag.repair_data', return_value=pd.DataFrame())
    mocker.patch('dags.eco2mix_etl_dag.clean_data', return_value=pd.DataFrame())
    mocker.patch('dags.eco2mix_etl_dag.del_excel_files')
    mocker.patch('dags.eco2mix_etl_dag.connect', return_value=connect())
    mocker.patch('dags.eco2mix_etl_dag.insert_data')

    ti = mocker.MagicMock()
    return {'ti': ti}

def test_extract_data(context):
    extract_data(**context)
    context['ti'].xcom_push.assert_called_once_with(
        key='date_info',
        value={'day': 1, 'month': 1, 'year': 2021}
    )

def test_transform_data(context):
    context['ti'].xcom_pull.return_value = {'day': 1, 'month': 1, 'year': 2021}
    transform_data(**context)
    context['ti'].xcom_pull.assert_called_once_with(key='date_info', task_ids='extract_data')
    context['ti'].xcom_push.assert_called_once_with(key='cleaned_df', value=pd.DataFrame())

def test_load_data(context):
    context['ti'].xcom_pull.return_value = pd.DataFrame()
    load_data(**context)
    context['ti'].xcom_pull.assert_called_once_with(key='cleaned_df', task_ids='transform_data')
