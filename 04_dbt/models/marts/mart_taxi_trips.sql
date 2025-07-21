-- Mart model for NYC taxi trips
-- Cleaned and transformed taxi data ready for analysis

{{ config(
    materialized='table',
    schema='mart'
) }}

SELECT 
    trip_id,
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    pickup_longitude,
    pickup_latitude,
    dropoff_longitude,
    dropoff_latitude,
    passenger_count,
    trip_distance,
    fare_amount,
    tip_amount,
    total_amount,
    payment_type,
    
    -- Derived fields
    DATE(pickup_datetime) as trip_date,
    EXTRACT(HOUR FROM pickup_datetime) as pickup_hour,
    CASE 
        WHEN trip_distance > 0 THEN fare_amount / trip_distance 
        ELSE 0 
    END as fare_per_mile,
    
    -- Location grouping (will be populated with actual zones)
    'unknown' as pickup_zone,
    'unknown' as dropoff_zone
    
FROM {{ ref('stg_taxi_trips') }}
WHERE trip_id != 'placeholder'  -- Filter out placeholder data
