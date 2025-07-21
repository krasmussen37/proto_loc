"""
Dagster definitions for proto_loc analytics platform

This module defines all Dagster assets for data ingestion and processing.
Following the standards defined in 00_clinerules/04_data_integration.md
"""

from dagster import Definitions, asset
import duckdb
import os
from pathlib import Path


@asset(description="Ingest NYC yellow taxi trip data from monthly Parquet files")
def raw_nyc_taxi_trips(context) -> None:
    """
    Combines all monthly yellow taxi Parquet files into a single raw table.
    
    Source: NYC TLC Yellow Taxi Trip Records
    Files: yellow_tripdata_YYYY-MM.parquet (Jan 2023 - May 2025)
    Output: raw.duckdb.nyc_taxi_data.raw_taxi_trips
    """
    raw_db_path = os.getenv("DUCKDB_RAW_PATH")
    if not raw_db_path:
        # Fallback for development
        base_path = Path(__file__).parent.parent
        raw_db_path = str(base_path / "02_duck_db" / "01_raw" / "raw.duckdb")
    
    # Ensure database directory exists
    Path(raw_db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = duckdb.connect(raw_db_path)
    
    try:
        # Create schema
        conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_taxi_data")
        
        # Ingest all Parquet files in one efficient operation
        conn.execute("""
            CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_trips AS 
            SELECT 
                *,
                CURRENT_TIMESTAMP as _ingested_at
            FROM read_parquet('/app/01_source_data/nyc_yellow_taxi_demo_data/yellow_cab_data_monthly/*.parquet')
        """)
        
        # Validation and logging
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_trips,
                MIN(tpep_pickup_datetime) as earliest_trip,
                MAX(tpep_pickup_datetime) as latest_trip,
                COUNT(DISTINCT DATE_TRUNC('month', tpep_pickup_datetime)) as months_of_data
            FROM nyc_taxi_data.raw_taxi_trips
        """).fetchone()
        
        context.log.info(
            f"Successfully loaded {stats[0]:,} taxi trips "
            f"from {stats[1]} to {stats[2]} "
            f"spanning {stats[3]} months"
        )
        
    except Exception as e:
        context.log.error(f"Failed to ingest taxi trips: {e}")
        raise
    finally:
        conn.close()


@asset(description="Ingest NYC taxi zone lookup data")
def raw_nyc_taxi_zones(context) -> None:
    """
    Loads taxi zone lookup data from CSV.
    
    Source: NYC TLC Taxi Zone Lookup Table
    File: taxi_zone_lookup.csv
    Output: raw.duckdb.nyc_taxi_data.raw_taxi_zones
    """
    raw_db_path = os.getenv("DUCKDB_RAW_PATH")
    if not raw_db_path:
        # Fallback for development
        base_path = Path(__file__).parent.parent
        raw_db_path = str(base_path / "02_duck_db" / "01_raw" / "raw.duckdb")
    
    # Ensure database directory exists
    Path(raw_db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = duckdb.connect(raw_db_path)
    
    try:
        # Ensure schema exists
        conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_taxi_data")
        
        # Load CSV with auto-detection
        conn.execute("""
            CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_zones AS 
            SELECT 
                *,
                CURRENT_TIMESTAMP as _ingested_at
            FROM read_csv_auto('/app/01_source_data/nyc_yellow_taxi_demo_data/taxi_zones/taxi_zone_lookup.csv')
        """)
        
        # Validation and logging
        result = conn.execute("""
            SELECT 
                COUNT(*) as zone_count,
                COUNT(DISTINCT "Borough") as borough_count
            FROM nyc_taxi_data.raw_taxi_zones
        """).fetchone()
        
        context.log.info(
            f"Successfully loaded {result[0]} taxi zones "
            f"across {result[1]} boroughs"
        )
        
    except Exception as e:
        context.log.error(f"Failed to ingest taxi zones: {e}")
        raise
    finally:
        conn.close()


# Define all assets for Dagster
defs = Definitions(
    assets=[
        raw_nyc_taxi_trips,
        raw_nyc_taxi_zones,
    ],
)
