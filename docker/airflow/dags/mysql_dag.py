import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from dateutil.parser import parse
from datetime import timezone
from airflow import DAG
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from air_quality_functions.process_data import map_column_to_hour
from air_quality_functions.retrieve_data import get_data

# Default arguments for the DAG
default_args = {
    'owner': 'aniqpremji',
    'start_date': datetime(2023, 7, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG instance
dag = DAG(
    'handle_data_upload',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

def query_latest_pm25(ti):
    hook = MySqlHook(mysql_conn_id='mysql_conn')
    query_pm25 = """SELECT
                        date_column,
                            CASE WHEN H23 IS NOT NULL THEN 'H23'
                                WHEN H22 IS NOT NULL THEN 'H22'	
                                WHEN H21 IS NOT NULL THEN 'H21'				
                                WHEN H20 IS NOT NULL THEN 'H20'
                                WHEN H19 IS NOT NULL THEN 'H19'
                                WHEN H18 IS NOT NULL THEN 'H18'
                                WHEN H17 IS NOT NULL THEN 'H17'
                                WHEN H16 IS NOT NULL THEN 'H16'
                                WHEN H15 IS NOT NULL THEN 'H15'
                                WHEN H14 IS NOT NULL THEN 'H14'
                                WHEN H13 IS NOT NULL THEN 'H13'
                                WHEN H12 IS NOT NULL THEN 'H12'
                                WHEN H11 IS NOT NULL THEN 'H11'
                                WHEN H10 IS NOT NULL THEN 'H10'
                                WHEN H09 IS NOT NULL THEN 'H09'
                                WHEN H08 IS NOT NULL THEN 'H08'
                                WHEN H07 IS NOT NULL THEN 'H07'
                                WHEN H06 IS NOT NULL THEN 'H06'
                                WHEN H05 IS NOT NULL THEN 'H05'
                                WHEN H04 IS NOT NULL THEN 'H04'
                                WHEN H03 IS NOT NULL THEN 'H03'
                                WHEN H02 IS NOT NULL THEN 'H02'
                                WHEN H01 IS NOT NULL THEN 'H01'
                                ELSE 'H00'
                                END AS last_non_empty_hour
                    FROM kitchener_pm25
                    WHERE date_column = (
                        SELECT MAX(date_column) FROM kitchener_pm25
                    );"""

    results = hook.get_records(query_pm25)

    for date, time in results:
        format_time = map_column_to_hour(time)
        new_datetime = datetime.combine(date, format_time)
    
    print(f'Datetime: {new_datetime}')
    dt_str = new_datetime.isoformat()
    ti.xcom_push(key = 'latest_pm25_datetime', value = dt_str)

def get_latest_pm25_result(ti):
    result = get_data(url = "https://api.openaq.org/v2/latest?parameter=pm25&parameter=o3&location=Kitchener",
            headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"})
    latest_datetime = ti.xcom_pull(task_ids = 'check_latest_pm25', key = 'latest_pm25_datetime')
    latest_datetime = datetime.strptime(latest_datetime, "%Y-%m-%dT%H:%M:%S")

    utc_datetime = parse(result['pm25']['last_updated']).astimezone(timezone.utc)
    formatted_datetime_str = utc_datetime.strftime("%Y-%m-%d %H:%M")
    new_datetime = datetime.strptime(formatted_datetime_str, "%Y-%m-%d %H:%M")

    time_diff = (new_datetime - latest_datetime).total_seconds()/3600
    print(f'Time diff: {time_diff} hours')
    

get_pm25_query_results_task = PythonOperator(
    task_id = 'check_latest_pm25',
    python_callable = query_latest_pm25,
    dag = dag
)

find_time_difference = PythonOperator(
    task_id = 'find_time_difference',
    python_callable=get_latest_pm25_result,
    dag=dag
)

get_pm25_query_results_task >> find_time_difference