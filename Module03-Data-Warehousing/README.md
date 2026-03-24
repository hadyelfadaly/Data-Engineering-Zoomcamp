# Homework

## Question 5 & 7 &  8 Answered in MCQ

## Quetions 1 - 4 & 6 & 9 Answered in MCQ and Below is the SQL Queries

```SQL
--creating materalized table for hw
CREATE TABLE zoomcamp_all_trips_data.yellow_taxi_regular AS
SELECT * FROM zoomcamp_all_trips_data.yellow_taxi_2024_external;

--QUESTION 1 in homework
SELECT COUNT(*) FROM zoomcamp_all_trips_data.yellow_taxi_2024_external;
--answer = 20,332,093

--QUESTION 2 in homework
SELECT COUNT(PULocationID) FROM zoomcamp_all_trips_data.yellow_taxi_2024_external;
--answer = 0MB
SELECT COUNT(PULocationID) FROM zoomcamp_all_trips_data.yellow_taxi_regular;
--answer = 155.12MB

--QUESTION 3 in homework
SELECT PULocationID FROM zoomcamp_all_trips_data.yellow_taxi_regular;
--answer = 155.12MB
SELECT PULocationID, DOLocationID FROM zoomcamp_all_trips_data.yellow_taxi_regular;
--answer = 310.24MB

--BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.

--QUESTION 4 in homework
SELECT COUNT(fare_amount)
FROM zoomcamp_all_trips_data.yellow_taxi_2024_external
WHERE fare_amount = 0;
--answer = 8,333

--create partitioned and clustered table for next questions
CREATE TABLE zoomcamp_all_trips_data.yellow_taxi_partitioned_clustered
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS SELECT * FROM zoomcamp_all_trips_data.yellow_taxi_2024_external;

--QUESTION 6 in homework
SELECT DISTINCT VendorID
FROM zoomcamp_all_trips_data.yellow_taxi_regular
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
--answer = 310.24MB
SELECT DISTINCT VendorID
FROM zoomcamp_all_trips_data.yellow_taxi_partitioned_clustered
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
--answer = 26.84MB

--QUESTION 9 in homework
SELECT count(*) FROM zoomcamp_all_trips_data.yellow_taxi_regular;
--answer = OMB, The query estimates 0 bytes will be read because BigQuery retrieves the exact row count directly from the table's pre-calculated metadata, entirely bypassing the need to scan the underlying data blocks.
```


