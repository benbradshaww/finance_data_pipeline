from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow')

from scripts.drop_table_scripts.drop_table import drop_table

default_args = {
    'owner': 'ben',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    default_args=default_args,
    dag_id='drop_table',
    description='Drop table workflow'
) as dag:

    task0 = PythonOperator(
        task_id='drop_table',
        python_callable=drop_table,
    )

    task0