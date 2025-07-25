{{
  config(
    materialized='table'
  )
}}

WITH stg_trips AS (
  SELECT * FROM {{ ref('stg_taxi_trips') }}
),

stg_zones AS (
  SELECT * FROM {{ ref('stg_taxi_zones') }}
),

dim_vendor AS (
  SELECT * FROM {{ ref('dim_vendor') }}
),

dim_rate_code AS (
  SELECT * FROM {{ ref('dim_rate_code') }}
),

dim_payment_type AS (
  SELECT * FROM {{ ref('dim_payment_type') }}
),

-- Filter trips to valid date range and join with dimensions
fact_trips AS (
  SELECT
    -- Primary trip data with proper type casting
    t.VendorID,
    t.RatecodeID,
    t.PULocationID,
    t.DOLocationID,
    t.payment_type,
    t.tpep_pickup_datetime,
    t.tpep_dropoff_datetime,
    t.passenger_count,
    t.trip_distance,
    t.fare_amount,
    t.extra,
    t.mta_tax,
    t.tip_amount,
    t.tolls_amount,
    t.improvement_surcharge,
    t.total_amount,
    t.congestion_surcharge,
    t.airport_fee,
    t.store_and_fwd_flag,
    t.calculated_total_amount,
    t.trip_duration_minutes,
    t.pickup_date,
    t.pickup_year,
    t.pickup_month,
    t.pickup_day_of_week,
    t.pickup_hour,
    
    -- Dimension attributes for easier analysis
    v.vendor_name,
    r.rate_code_name,
    pt.payment_name,
    
    -- Pickup location details
    pu_zone.Zone AS pickup_zone,
    pu_zone.Borough AS pickup_borough,
    pu_zone.service_zone AS pickup_service_zone,
    
    -- Dropoff location details  
    do_zone.Zone AS dropoff_zone,
    do_zone.Borough AS dropoff_borough,
    do_zone.service_zone AS dropoff_service_zone,
    
    -- Calculated metrics for analysis
    CASE
      WHEN t.trip_distance > 0 THEN t.fare_amount / t.trip_distance
      ELSE 0
    END AS fare_per_mile,
    
    CASE
      WHEN t.trip_duration_minutes > 0 THEN t.fare_amount / t.trip_duration_minutes
      ELSE 0
    END AS fare_per_minute,
    
    -- Data quality flags
    CASE 
      WHEN t.VendorID IS NULL THEN 1 
      ELSE 0 
    END AS missing_vendor_flag,
    
    CASE 
      WHEN t.trip_duration_minutes <= 0 THEN 1 
      ELSE 0 
    END AS negative_duration_flag,
    
    CASE 
      WHEN ABS(t.total_amount - t.calculated_total_amount) > 0.01 THEN 1 
      ELSE 0 
    END AS total_amount_mismatch_flag,
    
    -- Keep metadata
    t._ingested_at
    
  FROM stg_trips t
  
  -- Join with dimension tables (LEFT JOIN to preserve fact records even if dimension is missing)
  LEFT JOIN dim_vendor v ON t.VendorID = v.vendor_id
  LEFT JOIN dim_rate_code r ON t.RatecodeID = r.rate_code_id  
  LEFT JOIN dim_payment_type pt ON t.payment_type = pt.payment_type
  LEFT JOIN stg_zones pu_zone ON t.PULocationID = pu_zone.LocationID
  LEFT JOIN stg_zones do_zone ON t.DOLocationID = do_zone.LocationID
  
  -- Filter to valid date range to exclude erroneous records
  WHERE t.pickup_date >= DATE '2023-01-01' 
    AND t.pickup_date <= DATE '2025-05-31'
    
  -- Additional data quality filters
  AND t.trip_distance >= 0
  AND t.fare_amount >= 0
  AND t.passenger_count > 0
  AND t.passenger_count <= 6  -- reasonable upper bound for taxi
)

SELECT * FROM fact_trips
