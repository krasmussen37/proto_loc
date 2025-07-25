-- Mart model for NYC taxi trips
-- Cleaned and transformed taxi data ready for analysis

{{ config(
    materialized='table',
    schema='mart'
) }}

SELECT 
    -- Core trip information
    VendorID,
    tpep_pickup_datetime as pickup_datetime,
    tpep_dropoff_datetime as dropoff_datetime,
    PULocationID as pickup_location_id,
    DOLocationID as dropoff_location_id,
    passenger_count,
    trip_distance,
    
    -- Financial information
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    total_amount,
    congestion_surcharge,
    airport_fee,
    payment_type,
    
    -- Calculated fields
    calculated_total_amount,
    trip_duration_minutes,
    
    -- Derived time fields
    pickup_date,
    pickup_year,
    pickup_month,
    pickup_day_of_week,
    pickup_hour,
    
    -- Rate and service info
    RatecodeID,
    store_and_fwd_flag,
    
    -- Derived business metrics
    CASE 
        WHEN trip_distance > 0 THEN fare_amount / trip_distance 
        ELSE 0 
    END as fare_per_mile,
    
    CASE 
        WHEN trip_duration_minutes > 0 THEN fare_amount / trip_duration_minutes 
        ELSE 0 
    END as fare_per_minute,
    
    -- Data quality flags
    CASE 
        WHEN trip_duration_minutes < 0 THEN 1 
        ELSE 0 
    END as negative_duration_flag,
    
    CASE 
        WHEN ABS(total_amount - calculated_total_amount) > 0.01 THEN 1 
        ELSE 0 
    END as total_amount_mismatch_flag,
    
    -- Metadata
    _ingested_at
    
FROM {{ ref('stg_taxi_trips') }}
-- Filter to reasonable data ranges
WHERE pickup_date >= DATE '2023-01-01' 
  AND pickup_date <= DATE '2025-05-31'
  AND trip_distance >= 0
  AND fare_amount >= 0
  AND passenger_count > 0
