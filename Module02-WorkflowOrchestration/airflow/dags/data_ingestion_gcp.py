import os
import logging
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from google.cloud import storage
import pyarrow.csv as pv
import pyarrow.parquet as pq
from datetime import datetime

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCP_GCS_BUCKET")
DATASET_NAME = os.getenv("BIGQUERY_DATASET")
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
URL_PREFIX = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
URL_TEMPLATE = URL_PREFIX + "/yellow_tripdata_{{execution_date.strftime('%Y-%m')}}.csv.gz"
file_name = "output_{{execution_date.strftime('%Y-%m')}}.csv.gz"
OUTPUT_FILE_TEMPLATE = f"{AIRFLOW_HOME}/{file_name}"
parquet_file = file_name.replace('.csv.gz', '.parquet')
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'start_date':datetime(2021, 1, 1),
    'end_date':datetime(2021, 3, 31),
}

def format_to_parquet(src_file):

    if not src_file.endswith('.csv.gz'):

        logging.error("Can only accept source files in CSV format, for the moment")

        return

    table = pv.read_csv(src_file)

    pq.write_table(table, src_file.replace('.csv.gz', '.parquet'))

def upload_to_gcs(bucket_name, object_name, local_file):

    #WORKAROUND to prevent timeout for files > 5 MB on 800 kbps upload speed.
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


with DAG(
    dag_id="GCPIngestionDag",
    schedule_interval="@Monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    tags=['DE-Z']
) as dag:

    download_data = BashOperator(
        task_id="download_data",
        bash_command=f"curl -sSLf {URL_TEMPLATE} > {OUTPUT_FILE_TEMPLATE}"
    )
    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet",
        python_callable=format_to_parquet,
        op_kwargs=dict(src_file=OUTPUT_FILE_TEMPLATE)
    )
    upload_bucket = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket_name=BUCKET_NAME,
            object_name=f"raw/{parquet_file}",
            local_file=OUTPUT_FILE_TEMPLATE.replace('.csv.gz', '.parquet')
        )
    )
    create_external_table = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": DATASET_NAME,
                "tableId": "external_table"
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET_NAME}/raw/{parquet_file}"]
            }
        }
    )
    cleanup_task = BashOperator(
        task_id="cleanup",
        bash_command=f"rm -f {OUTPUT_FILE_TEMPLATE} {OUTPUT_FILE_TEMPLATE.replace('.csv.gz', '.parquet')}"
    )

    download_data >> format_to_parquet_task >> upload_bucket >> create_external_table >> cleanup_task