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
from air_quality_functions.process_data import map_column_to_hour, map_hour_to_column
from air_quality_functions.retrieve_data import get_data

# Default arguments for the DAG
default_args = {
    'owner': 'aniqpremji',
    'start_date': datetime(2023, 7, 22),
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
    """
        Method to retrieve the latest date, and the name of the column with the latest time from the database
    """
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

    (pm25_date, pm25_time) = results[0]
    format_time = map_column_to_hour(pm25_time)
    new_datetime = datetime.combine(pm25_date, format_time)
    
    print(f'Datetime: {new_datetime}')
    dt_str = new_datetime.isoformat()
    pm25_date_str = pm25_date.isoformat()

    ti.xcom_push(key = 'latest_pm25_date_col', value = pm25_date_str)
    ti.xcom_push(key = 'latest_pm25_time_col', value = pm25_time)
    ti.xcom_push(key = 'latest_pm25_datetime', value = dt_str)

def get_latest_pm25_api(ti):
    """
        Get latest information from the OpenAQ api
    """
    latest_api = get_data(url = "https://api.openaq.org/v2/latest?parameter=pm25&parameter=o3&location=Kitchener",
            headers = {"accept": "application/json", "X-API-Key": "bf94e16e413120ef454855fc046f5018c262c450b0ee9e976e31b4f5fad116e9"})
    ti.xcom_push(key = 'latest_api', value = latest_api)    

def get_value_for_latest_pm25(ti):
    """
        For previously defined latest date and time, get pm25 value
    """
    hook = MySqlHook(mysql_conn_id='mysql_conn')
    latest_pm25_date = ti.xcom_pull(task_ids = 'check_latest_pm25', key = 'latest_pm25_date_col')
    latest_pm25_date = datetime.strptime(latest_pm25_date, "%Y-%m-%d").date()
    latest_pm25_time_col = ti.xcom_pull(task_ids = 'check_latest_pm25', key = 'latest_pm25_time_col')

    # Protect against SQL injections
    valid_columns = [f'H{i:02d}' for i in range(24)]
    if latest_pm25_time_col not in valid_columns:
        raise ValueError(f"Invalid column name: {latest_pm25_time_col}")

    query_latest_value = f"""
        SELECT {latest_pm25_time_col} FROM kitchener_pm25
        WHERE date_column = %s
    """

    result = hook.get_first(query_latest_value, parameters=(latest_pm25_date,))[0]

    ti.xcom_push(key = 'latest_pm25_value', value = result)

def find_time_difference(ti):
    result = ti.xcom_pull(task_ids = 'get_latest_result', key ='latest_api')
    latest_datetime = ti.xcom_pull(task_ids = 'check_latest_pm25', key = 'latest_pm25_datetime')
    latest_datetime = datetime.strptime(latest_datetime, "%Y-%m-%dT%H:%M:%S")

    utc_datetime = parse(result['pm25']['last_updated']).astimezone(timezone.utc)
    formatted_datetime_str = utc_datetime.strftime("%Y-%m-%d %H:%M")
    new_datetime = datetime.strptime(formatted_datetime_str, "%Y-%m-%d %H:%M")

    time_diff = str((new_datetime - latest_datetime).total_seconds()/3600)
    print(f'Time diff: {time_diff} hours')

    ti.xcom_push(key = 'time_diff', value = time_diff)
    
def handle_data_upload(ti, **kwargs):
    hook = MySqlHook(mysql_conn_id='mysql_conn')
    
    latest_api_value = ti.xcom_pull(task_ids = 'check_latest_pm25_value', key = 'latest_pm25_value')
    
    latest_pm25_datetime = ti.xcom_pull(task_ids = 'check_latest_pm25', key = 'latest_pm25_datetime')
    latest_pm25_datetime = datetime.strptime(latest_pm25_datetime, "%Y-%m-%dT%H:%M:%S")
    
    time_diff = int(ti.xcom_pull(task_ids = 'find_pm25_time_difference', key = 'time_diff'))

    new_datetime = latest_pm25_datetime + timedelta(hours = 1.0)
    new_date = new_datetime.date
    new_time = new_datetime.time()
    new_time_col = map_hour_to_column(new_time)

    if time_diff <= 1:
        simple_update_query = f"""
                UPDATE kitchener_pm25
                SET {new_time_col} = %s
                WHERE date_column = %s
            """
        hook.run(simple_update_query, parameters=(latest_api_value, new_date))
    else:
        pass
    
get_pm25_query_col_task = PythonOperator(
    task_id = 'check_latest_pm25',
    python_callable = query_latest_pm25,
    dag = dag
)

get_pm25_query_value_task = PythonOperator(
    task_id = 'check_latest_pm25_value',
    python_callable = get_value_for_latest_pm25,
    dag = dag
)

get_latest_pm25_api_task = PythonOperator(
    task_id = 'get_latest_pm25_api',
    python_callable=get_latest_pm25_api,
    dag=dag
)

find_time_difference_task = PythonOperator(
    task_id = 'find_pm25_time_difference',
    python_callable=find_time_difference,
    dag=dag
)

get_pm25_query_col_task >> get_pm25_query_value_task >> get_latest_pm25_api_task >> find_time_difference_task