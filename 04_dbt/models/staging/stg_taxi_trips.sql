-- Staging model for NYC taxi trips
-- This is a placeholder that will be populated with actual taxi data

{{ config(
    materialized='view',
    schema='stg'
) }}

SELECT 
    -- Trip identifiers
    'placeholder' as trip_id,
    'placeholder' as vendor_id,
    
    -- Timestamps
    CURRENT_TIMESTAMP as pickup_datetime,
    CURRENT_TIMESTAMP as dropoff_datetime,
    
    -- Location data
    0.0 as pickup_longitude,
    0.0 as pickup_latitude,
    0.0 as dropoff_longitude,
    0.0 as dropoff_latitude,
    
    -- Trip metrics
    1 as passenger_count,
    0.0 as trip_distance,
    0.0 as fare_amount,
    0.0 as tip_amount,
    0.0 as total_amount,
    
    -- Additional fields
    'placeholder' as payment_type,
    0.0 as pickup_longitude_raw,
    0.0 as pickup_latitude_raw,
    0.0 as dropoff_longitude_raw,
    0.0 as dropoff_latitude_raw
    
WHERE 1=0  -- Empty table for now
