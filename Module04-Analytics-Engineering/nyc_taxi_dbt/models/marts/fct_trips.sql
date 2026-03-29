{{
  config(
    materialized='incremental',
    unique_key='trip_id',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'  )
}}


SELECT 

    -- identifiers
    t.trip_id,
    t.vendor_id,
    t.service_type,
    t.rate_code_id,

    -- location info
    t.pickup_location_id,
    p.borough AS pickup_borough,
    p.zone AS pickup_zone,
    t.dropoff_location_id,
    d.borough AS dropoff_borough,
    d.zone AS dropoff_zone,
    
    -- trip timing
    t.pickup_datetime,
    t.dropoff_datetime,
    t.store_and_fwd_flag,

    -- trip metrics
    t.passenger_count,
    t.trip_distance,
    t.trip_type,
    {{get_trip_duration_minutes('t.pickup_datetime', 't.dropoff_datetime')}} as trip_duration_minutes,

    -- payment details
    
    t.fare_amount,
    t.extra,
    t.mta_tax,
    t.tip_amount,
    t.tolls_amount,
    t.ehail_fee,
    t.improvement_surcharge,
    t.total_amount,
    t.payment_type,
    t.payment_type_description

FROM {{ref('int_trips')}} t
LEFT JOIN {{ref('dim_zones')}} p
ON t.pickup_location_id = p.location_id
LEFT JOIN {{ref('dim_zones')}} d
ON t.dropoff_location_id = d.location_id

{% if is_incremental() %}

WHERE t.pickup_datetime >= (SELECT MAX(pickup_datetime) FROM {{this}})

{% endif %}