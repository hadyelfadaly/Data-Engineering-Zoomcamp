WITH green_taxi_trips AS (
    SELECT *, 'Green' AS service_type FROM {{ref('stg_green_taxi_trips')}}
),
yellow_taxi_trips AS (
    SELECT *, 'Yellow' AS service_type FROM {{ref('stg_yellow_taxi_trips')}}
)

SELECT * FROM green_taxi_trips
UNION ALL
SELECT * FROM yellow_taxi_trips
