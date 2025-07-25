{{
  config(
    materialized='view'
  )
}}

WITH source AS (
  SELECT * FROM {{ source('nyc_taxi_data', 'raw_taxi_zones') }}
),

transformed AS (
  SELECT
    -- Cast LocationID to string for consistency with trip data
    CAST(LocationID AS VARCHAR) AS LocationID,
    
    -- Clean and standardize text fields
    TRIM(Zone) AS Zone,
    TRIM(Borough) AS Borough,
    
    -- Cast service_zone to string (appears to be categorical)
    CAST(service_zone AS VARCHAR) AS service_zone,
    
    -- Keep ingestion metadata
    _ingested_at
    
  FROM source
)

SELECT * FROM transformed
