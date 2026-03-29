SELECT 
    -- identifiers
    CAST(Vendor_ID AS INTEGER) AS vendor_id,
    CAST(ratecode_id AS INTEGER) AS rate_code_id,
    CAST(PU_Location_ID AS INTEGER) AS pickup_location_id,
    CAST(DO_Location_ID AS INTEGER) AS dropoff_location_id,

    -- timestamps
    CAST(tpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
    CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,

    -- trip info
    store_and_fwd_flag,
    CAST(passenger_count AS INTEGER) AS passenger_count,
    CAST(trip_distance AS FLOAT64) AS trip_distance,
    CAST(1 AS INTEGER) AS trip_type, -- yellow taxi trips don't have a trip type column, so we will just hardcode it to 1 for all rows

    -- payment info
    CAST(fare_amount AS NUMERIC) AS fare_amount,
    CAST(extra AS NUMERIC) AS extra,
    CAST(mta_tax AS NUMERIC) AS mta_tax,
    CAST(tip_amount AS NUMERIC) AS tip_amount,
    CAST(tolls_amount AS NUMERIC) AS tolls_amount,
    CAST(improvement_surcharge AS NUMERIC) AS improvement_surcharge,
    CAST(0 AS NUMERIC) AS ehail_fee, -- yellow taxi trips don't have an ehail fee column, so we will just hardcode it to 0 for all rows
    CAST(total_amount AS NUMERIC) AS total_amount,
    CAST(payment_type AS INTEGER) AS payment_type,
FROM {{source('raw_data', 'yellow_taxi_trips') }}
WHERE vendor_id IS NOT NULL