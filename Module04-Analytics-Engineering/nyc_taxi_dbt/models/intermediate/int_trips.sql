with unioned AS (
    SELECT * FROM {{ref('int_trips_unioned')}}
),
payment_type AS (
    SELECT * FROM {{ref('payment_type_lookup')}}
),
cleaned_enriched AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['u.vendor_id', 'u.pickup_datetime', 'u.pickup_location_id', 'u.service_type']) }} as trip_id,

        -- Identifiers
        u.vendor_id,
        u.service_type,
        u.rate_code_id,

        -- Location IDs
        u.pickup_location_id,
        u.dropoff_location_id,

        -- Timestamps
        u.pickup_datetime,
        u.dropoff_datetime,

        -- Trip details
        u.store_and_fwd_flag,
        u.passenger_count,
        u.trip_distance,
        u.trip_type,

        -- Payment breakdown
        u.fare_amount,
        u.extra,
        u.mta_tax,
        u.tip_amount,
        u.tolls_amount,
        u.ehail_fee,
        u.improvement_surcharge,
        u.total_amount,

        -- Enrich with payment type description
        coalesce(u.payment_type, 0) as payment_type,
        coalesce(p.description, 'Unknown') as payment_type_description
        
    FROM unioned u
    LEFT JOIN payment_type p
    ON u.payment_type = p.payment_type
)

SELECT * FROM cleaned_enriched
QUALIFY row_number() OVER (PARTITION BY vendor_id, pickup_datetime, pickup_location_id, service_type
 ORDER BY dropoff_datetime DESC) = 1
-- filter out duplicates by keeping the most recent dropoff_datetime for each unique trip defined by vendor_id, 
--pickup_datetime, pickup_location_id, and service_type