{{
  config(
    materialized='view'
  )
}}

WITH source AS (
  SELECT * FROM {{ source('nyc_taxi_data', 'raw_taxi_trips') }}
),

transformed AS (
  SELECT
    -- Cast ID columns to strings for proper categorical handling
    CAST(VendorID AS VARCHAR) AS VendorID,
    CAST(RatecodeID AS VARCHAR) AS RatecodeID,
    CAST(PULocationID AS VARCHAR) AS PULocationID,
    CAST(DOLocationID AS VARCHAR) AS DOLocationID,
    CAST(payment_type AS VARCHAR) AS payment_type,
    
    -- Convert timestamps to proper TIMESTAMP type (assuming NYC local time)
    CAST(tpep_pickup_datetime AS TIMESTAMP) AS tpep_pickup_datetime,
    CAST(tpep_dropoff_datetime AS TIMESTAMP) AS tpep_dropoff_datetime,
    
    -- Keep numeric fields as-is
    passenger_count,
    trip_distance,
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    total_amount,
    congestion_surcharge,
    airport_fee,
    
    -- Store and forward flag
    store_and_fwd_flag,
    
    -- Calculate total amount for validation based on data dictionary
    -- Components: fare_amount + extra + mta_tax + improvement_surcharge + tolls_amount + congestion_surcharge + airport_fee
    -- Note: tip_amount is NOT included per data dictionary, cbd_congestion_fee not present in our dataset
    (
      COALESCE(fare_amount, 0) +
      COALESCE(extra, 0) +
      COALESCE(mta_tax, 0) +
      COALESCE(improvement_surcharge, 0) +
      COALESCE(tolls_amount, 0) +
      COALESCE(congestion_surcharge, 0) +
      COALESCE(airport_fee, 0)
    )::DECIMAL(10,2) AS calculated_total_amount,
    
    -- Calculate trip duration in minutes
    DATEDIFF('minute', 
      CAST(tpep_pickup_datetime AS TIMESTAMP), 
      CAST(tpep_dropoff_datetime AS TIMESTAMP)
    ) AS trip_duration_minutes,
    
    -- Extract date parts for easier analysis
    DATE(CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_date,
    EXTRACT(YEAR FROM CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_year,
    EXTRACT(MONTH FROM CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_month,
    EXTRACT(DOW FROM CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_day_of_week,
    EXTRACT(HOUR FROM CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_hour,
    
    -- Keep ingestion metadata
    _ingested_at
    
  FROM source
)

SELECT * FROM transformed
