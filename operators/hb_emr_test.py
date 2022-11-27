import airflow
from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.models import Variable

aws_access_key_id = Variable.get('AWSAccessKeyId')
aws_secret_access_key = Variable.get('AWSSecretKey')

default_args = {
    'owner': 'hyobae',
    'email': ['lhb08030803@gmail.com'],
    'depends_on_past': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(year=2022, month=6, day=1),
}

dag = DAG(
    dag_id='emr-test-dag-HB',
    default_args=default_args,
    schedule_interval='5 0 * * *',
    max_active_runs=1,
    tags=["lhb"],
)

ssh_task = SSHOperator(
    task_id='ssh_task',
    ssh_conn_id='ssh_pipeliner',
    command='''echo "Hello World" > hb/hb.txt''',
    dag=dag
)

test_emr_job = SSHOperator(
    task_id='emr_pi_job',
    ssh_conn_id='ssh_pipeliner',
    command="spark-submit --deploy-mode cluster s3://pipeliner-kwon/emr/pi.py",
    dag=dag
)

ssh_task >> test_emr_job