# Module 2: Workflow Orchestration

## Overview
This directory contains the code and configuration for Module 2 of the Data Engineering Zoomcamp. The core objective of this module was to build an automated, scheduled Data Lake pipeline using Apache Airflow, transferring data from the web into Google Cloud Platform (GCP).

## Technologies Used
* **Orchestration:** Apache Airflow
* **Containerization:** Docker & Docker Compose
* **Cloud Infrastructure:** Google Cloud Storage (GCS) & Google BigQuery
* **Language:** Python
* **Data Format:** Parquet

## Pipeline Architecture
The Airflow DAG (`mod3HWDag.py`) performs the following automated steps on a scheduled basis:
1. **Extraction:** Downloads monthly New York City Taxi trip data (Yellow Taxi) natively in Parquet format.
2. **Cloud Load:** Uploads the raw Parquet files directly into a GCS bucket (Data Lake).
3. **Data Warehouse Integration:** Automatically creates and updates an External Table in BigQuery pointing to the wildcard Parquet files in the GCS bucket.
4. **Cleanup:** Executes a bash operator to safely remove the local files from the Airflow worker to preserve storage space.

## Key Learnings & Challenges Overcome
* Configured Airflow via Docker Compose and managed volume mounts for secure GCP service account key integration (`.google/credentials`).
* Overcame common Airflow scheduling pitfalls (e.g., `execution_date` vs `logical_date` deprecations, strict case-sensitivity in cron intervals).
* Handled memory and storage optimizations within a WSL2 environment to prevent hidden swap-file bloat.
* Handled connection drops during data upload using Airflow's built-in retry mechanisms and idempotency.
