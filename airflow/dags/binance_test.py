from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

from operators import binance_to_s3

aws_access_key_id = Variable.get('AWSAccessKeyId')
aws_secret_access_key = Variable.get('AWSSecretKey')

default_args = {
    'owner': 'hyobae',
    'email': ['lhb08030803@gmail.com'],
    'depends_on_past': False,
    'retries': 8,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(year=2022, month=4, day=1),
}

dag = DAG(
    dag_id='hb_binance_test',
    default_args=default_args,
    schedule_interval='5 0 * * *',
    max_active_runs=1,
)

extract_task = PythonOperator(
    task_id='extract',
    python_callable=binance_to_s3.extract,
    provide_context=True,
    op_kwargs = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'bucket_name': 'binance-by-local-airflow'
    },
    dag=dag
)

transform_and_load_task = PythonOperator(
    task_id='transform_and_load',
    python_callable=binance_to_s3.transform_and_load,
    provide_context=True,
    op_kwargs = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'bucket_name': 'binance-by-local-airflow'
    },
    dag=dag
)

extract_task >> transform_and_load_task