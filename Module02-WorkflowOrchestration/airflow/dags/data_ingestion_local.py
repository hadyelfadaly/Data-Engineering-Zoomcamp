import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from ingest_script import run

local_workflow = DAG(
    "LocalIngestDag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 3, 31),
    catchup=True
)

#we will parameterize the url and the output file path using environment variables
#so not every month we will have to change the code, we will just change the environment variables
#we will use execution date to parameterize the file and the output file path, so we will have a different url and output file path for each execution date
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
URL_PREFIX = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
URL_TEMPLATE = URL_PREFIX + "/yellow_tripdata_{{execution_date.strftime('%Y-%m')}}.csv.gz"
OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + "/output_{{execution_date.strftime('%Y-%m')}}.csv.gz"
TABLE_NAME_TEMPLATE = "yellow_taxi_trips_{{execution_date.strftime('%Y_%m')}}"
#the blue part is using jinja template to replace the URL_PREFIX with the actual value of the environment variable

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")

with local_workflow:
    wget_task = BashOperator(
        task_id="wget",
        bash_command=f'curl -sSLf {URL_TEMPLATE} > {OUTPUT_FILE_TEMPLATE}'
    )
    ingest_task = PythonOperator(
        task_id="ingest",
        python_callable=run,
        op_kwargs=dict( 
            pg_user=PG_USER,
            pg_pass=PG_PASSWORD,
            pg_host=PG_HOST,
            pg_port=PG_PORT,
            pg_db=PG_DATABASE,
            table_name=TABLE_NAME_TEMPLATE,
            chunk_size=10000,
            csv_file=OUTPUT_FILE_TEMPLATE
        )
    )
    cleanup_task = BashOperator(
        task_id="cleanup",
        bash_command=f"rm -f {OUTPUT_FILE_TEMPLATE}"
    )
    
    wget_task >> ingest_task >> cleanup_task