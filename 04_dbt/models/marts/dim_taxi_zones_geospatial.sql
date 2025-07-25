{{
  config(
    materialized='table',
    pre_hook=[
      "INSTALL spatial;",
      "LOAD spatial;"
    ]
  )
}}

WITH taxi_zones_base AS (
  SELECT * FROM {{ ref('stg_taxi_zones') }}
),

-- Read shapefile data and convert to geospatial format
taxi_zones_spatial AS (
  SELECT
    CAST(LocationID AS VARCHAR) AS LocationID,
    Zone,
    Borough,
    service_zone,
    ST_AsText(geom) AS geometry_wkt,
    ST_AsGeoJSON(geom) AS geometry_geojson,
    ST_Area(geom) AS zone_area_sq_meters,
    ST_Centroid(geom) AS zone_centroid
  FROM ST_Read('{{ var("TAXI_ZONES_SHP_PATH") }}')
),

-- Join base taxi zone data with spatial data
final AS (
  SELECT
    b.LocationID,
    b.Zone,
    b.Borough,
    b.service_zone,
    s.geometry_wkt,
    s.geometry_geojson,
    s.zone_area_sq_meters,
    ST_X(s.zone_centroid) AS zone_centroid_longitude,
    ST_Y(s.zone_centroid) AS zone_centroid_latitude,
    b._ingested_at
  FROM taxi_zones_base b
  LEFT JOIN taxi_zones_spatial s ON b.LocationID = s.LocationID
)

SELECT * FROM final
