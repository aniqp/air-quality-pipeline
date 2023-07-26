import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from air_quality_functions.retrieve_data import get_data

default_args = {
    'owner': 'aniqpremji',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='s3_dag_new',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2023, 7, 7),
    catchup=False
) as dag:

    def retrieve_data():
        data = get_data()
        return data

    def upload_to_s3(ti):
        s3_hook = S3Hook(aws_conn_id='s3_conn')
        data = ti.xcom_pull(task_ids="retrieve_data_task")
        json_data = json.dumps(data)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"data_{timestamp}.json"
        s3_hook.load_string(string_data=json_data, key=f'new_data/{file_name}', bucket_name='air-quality-project')

    fetched_data = PythonOperator(
        task_id='retrieve_data_task',
        python_callable=retrieve_data
    )

    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3_task',
        python_callable=upload_to_s3
    )

    fetched_data >> upload_to_s3_task