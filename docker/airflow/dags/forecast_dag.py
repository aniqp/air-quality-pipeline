import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta, date
from dateutil.parser import parse
from datetime import timezone
from airflow import DAG
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from air_quality_functions.process_data import map_column_to_hour, map_hour_to_column, process_utc_string
from air_quality_functions.retrieve_data import get_data, backfill_data
from air_quality_functions.forecast_data import train_model

default_args = {
    'owner': 'aniqpremji',
    'start_date': '2023-07-28',
    'retries': 3,
    'retry_delay': timedelta(minutes=7),
}

# Create the DAG instance
dag = DAG(
    'forecast_dag',
    default_args=default_args,
    schedule_interval='7 4 * * *',
    catchup = False,
)

def retrieve_training_data(ti):
    hook = MySqlHook(mysql_conn_id='mysql_conn')
    query_training = "SELECT * FROM kitchener_pm25 WHERE date_column >= '2023-05-29'"
    results = hook.get_records(query_training)

    ti.xcom_push(key = 'training_data', value = results)

def train_predict_model(ti):
    data = ti.xcom_pull(task_ids = 'retrieve_training_data', key = 'training_data')
    next_date, predictions = train_model(data)
    hook = MySqlHook(mysql_conn_id='mysql_conn')
    original_date = datetime.now(timezone.utc) - timedelta(days = 1)
    original_date = original_date.date()
    values = predictions
    values.insert(0, next_date)
    values.append(original_date)
    values = tuple(values)
    print(f'Values: {values}, len values: {len(values)}')
    query_insert_predictions = "INSERT INTO kitchener_pm25_forecast VALUES %s"
    hook.run(query_insert_predictions, parameters=(values,))

retrieve_training_data_task = PythonOperator(
    task_id = 'retrieve_training_data',
    python_callable = retrieve_training_data,
    dag = dag
)

train_predict_model_task = PythonOperator(
    task_id = 'task_predict_model',
    python_callable = train_predict_model,
    dag = dag
)

retrieve_training_data_task >> train_predict_model_task