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
URL_PREFIX = "https://d37ci6vzurychx.cloudfront.net/trip-data"
URL_TEMPLATE = URL_PREFIX + "/yellow_tripdata_{{execution_date.strftime('%Y-%m')}}.parquet"
parquet_file = "yellow_tripdata_{{execution_date.strftime('%Y-%m')}}.parquet"
OUTPUT_FILE_TEMPLATE = f"{AIRFLOW_HOME}/{parquet_file}"
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'start_date':datetime(2024, 1, 1),
    'end_date':datetime(2024, 6, 30),
}


def upload_to_gcs(bucket_name, object_name, local_file):

    #WORKAROUND to prevent timeout for files > 5 MB on 800 kbps upload speed.
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


with DAG(
    dag_id="mod3HWDag",
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
    upload_bucket = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket_name=BUCKET_NAME,
            object_name=f"raw/{parquet_file}",
            local_file=OUTPUT_FILE_TEMPLATE
        )
    )
    create_external_table = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": DATASET_NAME,
                "tableId": "yellow_taxi_2024_external"
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET_NAME}/raw/yellow_tripdata_2024-*.parquet"]
            }
        }
    )
    cleanup_task = BashOperator(
        task_id="cleanup",
        bash_command=f"rm -f {OUTPUT_FILE_TEMPLATE}"
    )

    download_data >> upload_bucket >> create_external_table >> cleanup_task