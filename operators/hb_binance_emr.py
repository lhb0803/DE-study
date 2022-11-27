import airflow
from datetime import datetime,timedelta
from airflow import DAG
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

import binance

aws_access_key_id = Variable.get('AWSAccessKeyId2')
aws_secret_access_key = Variable.get('AWSSecretAccessKey2')

default_args = {
    'owner': 'hyobae',
    'depends_on_past': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(year=2022, month=6, day=24),
}

dag = DAG(
    dag_id='hb_binance_emr',
    default_args=default_args,
    schedule_interval='0 8 * * *',
    max_active_runs=1,
    tags=["lhb", "binance"],
)

extract = PythonOperator(
    task_id='extract',
    python_callable=binance.extract_binance_daily,
    provide_context=True,
    op_kwargs = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'bucket_name': 'pipeliner-hb'
    },
    dag=dag
)

transform_as_parquet = PythonOperator(
    task_id='transform_as_parquet',
    python_callable=binance.transform_as_parquet,
    provide_context=True,
    op_kwargs = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'bucket_name': 'pipeliner-hb'
    },
    dag=dag
)

spark_job = SSHOperator(
    task_id="emr_count_job",
    ssh_conn_id="ssh_pipeliner",
    command="spark-submit --deploy-mode cluster s3://pipeliner-hb/emr/hb_binance_count.py",
    dag=dag
)

extract >> transform_as_parquet >> spark_job