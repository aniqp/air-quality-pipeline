from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'aniqpremji',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
        
}

def greet(ti):
    first_name = ti.xcom_pull(task_ids = 'get_name', key = 'first_name')
    last_name = ti.xcom_pull(task_ids = 'get_name', key = 'last_name')
    age = ti.xcom_pull(task_ids = 'get_age', key = 'age')
    print(f'hello world, my name is {first_name} {last_name} and I am {age} years old')

def get_name(ti):
    ti.xcom_push(key = 'first_name', value = 'Jerry')
    ti.xcom_push(key = 'last_name', value = 'Fridman')

def get_age(ti):
    ti.xcom_push(key = 'age', value = 40)

with DAG(
    default_args = default_args,
    dag_id = 'test_python_dag_v7',
    description = 'First dag with Python operator',
    start_date = datetime(2023, 7, 2),
    schedule_interval = '@daily'
) as dag:
    task1 = PythonOperator(
        task_id = 'greet',
        python_callable = greet,
        # op_kwargs = {'age': 30}
    )
    task2 = PythonOperator(
        task_id = 'get_name',
        python_callable=get_name        
    )

    task3 = PythonOperator(
        task_id = 'get_age',
        python_callable=get_age
    )

    # Task2 and task3 are upstream of task1
    [task2, task3] >> task1