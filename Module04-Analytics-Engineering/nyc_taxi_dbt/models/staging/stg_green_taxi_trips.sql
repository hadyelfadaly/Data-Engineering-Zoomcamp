SELECT 
    -- identifiers
    CAST(Vendor_ID AS INTEGER) AS vendor_id,
    {{safe_cast('ratecode_id', 'integer')}} as rate_code_id,
    CAST(PU_Location_ID AS INTEGER) AS pickup_location_id,
    CAST(DO_Location_ID AS INTEGER) AS dropoff_location_id,

    -- timestamps
    CAST(lpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
    CAST(lpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,

    -- trip info
    store_and_fwd_flag,
    CAST(passenger_count AS INTEGER) AS passenger_count,
    CAST(trip_distance AS FLOAT64) AS trip_distance,
    {{safe_cast('trip_type', 'INTEGER')}} AS trip_type,

    -- payment info
    CAST(fare_amount AS NUMERIC) AS fare_amount,
    CAST(extra AS NUMERIC) AS extra,
    CAST(mta_tax AS NUMERIC) AS mta_tax,
    CAST(tip_amount AS NUMERIC) AS tip_amount,
    CAST(tolls_amount AS NUMERIC) AS tolls_amount,
    CAST(ehail_fee AS NUMERIC) AS ehail_fee,
    CAST(improvement_surcharge AS NUMERIC) AS improvement_surcharge,
    CAST(total_amount AS NUMERIC) AS total_amount,
    {{safe_cast('payment_type', 'integer')}} AS payment_type,
FROM {{source('raw_data', 'green_taxi_trips') }}
WHERE vendor_id IS NOT NULL