"""
Dagster definitions for proto_loc analytics platform

This file contains the data pipeline definitions for the platform.
NYC Taxi data ingestion and validation assets.

Key Design Principles:
- Robust connection management with proper cleanup to prevent database locks
- Retry logic for handling concurrent access conflicts
- Clear separation between raw data ingestion and validation
- Environment-aware database path configuration
"""

import os
import time
import pandas as pd
import duckdb
from dagster import asset, AssetExecutionContext


def connect_with_retry(db_path: str, read_only: bool = False, max_retries: int = 3, retry_delay: float = 1.0):
    """
    Connect to DuckDB with retry logic to handle lock conflicts.
    
    Args:
        db_path: Path to the DuckDB database file
        read_only: Whether to open in read-only mode
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retry attempts in seconds
        
    Returns:
        DuckDB connection object
        
    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            conn = duckdb.connect(db_path, read_only=read_only)
            return conn
        except Exception as e:
            if "lock" in str(e).lower() and attempt < max_retries - 1:
                print(f"🔄 Database lock detected (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff
                continue
            else:
                raise e

@asset(group_name="raw_data_ingestion")
def taxi_trips_raw(context: AssetExecutionContext) -> None:
    """
    Load NYC taxi trips data into raw DuckDB.
    Expected source: 01_source_data/taxi_trips.parquet
    """
    
    # File paths
    source_file = "/app/01_source_data/taxi_trips.parquet"
    raw_db_path = os.getenv("DUCKDB_RAW_PATH", "/app/02_duck_db/01_raw/raw.duckdb")
    
    context.log.info(f"Loading taxi trips from {source_file}")
    
    # Connect to raw DuckDB with retry logic
    conn = connect_with_retry(raw_db_path, read_only=False)
    
    try:
        # Create schema if not exists
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        
        # Check if source file exists
        if os.path.exists(source_file):
            # Load parquet file directly into DuckDB
            conn.execute(f"""
                CREATE OR REPLACE TABLE raw.taxi_trips AS 
                SELECT * FROM read_parquet('{source_file}')
            """)
            
            # Get row count
            row_count = conn.execute("SELECT COUNT(*) FROM raw.taxi_trips").fetchone()[0]
            context.log.info(f"✅ Loaded {row_count} taxi trip records into raw.taxi_trips")
            
        else:
            context.log.warning(f"⚠️ Source file not found: {source_file}")
            # Create empty table with expected schema
            conn.execute("""
                CREATE OR REPLACE TABLE raw.taxi_trips (
                    pickup_datetime TIMESTAMP,
                    dropoff_datetime TIMESTAMP,
                    pickup_locationid INTEGER,
                    dropoff_locationid INTEGER,
                    trip_distance DOUBLE,
                    fare_amount DOUBLE,
                    total_amount DOUBLE,
                    payment_type INTEGER,
                    passenger_count INTEGER
                )
            """)
            context.log.info("Created empty taxi_trips table with expected schema")
            
    finally:
        conn.close()

@asset(group_name="raw_data_ingestion")
def taxi_zones_raw(context: AssetExecutionContext) -> None:
    """
    Load NYC taxi zones lookup data into raw DuckDB.
    Expected source: 01_source_data/taxi_zones.csv
    """
    
    # File paths
    source_file = "/app/01_source_data/taxi_zones.csv"
    raw_db_path = os.getenv("DUCKDB_RAW_PATH", "/app/02_duck_db/01_raw/raw.duckdb")
    
    context.log.info(f"Loading taxi zones from {source_file}")
    
    # Connect to raw DuckDB with retry logic
    conn = connect_with_retry(raw_db_path, read_only=False)
    
    try:
        # Create schema if not exists
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        
        # Check if source file exists
        if os.path.exists(source_file):
            # Load CSV file directly into DuckDB
            conn.execute(f"""
                CREATE OR REPLACE TABLE raw.taxi_zones AS 
                SELECT * FROM read_csv_auto('{source_file}')
            """)
            
            # Get row count
            row_count = conn.execute("SELECT COUNT(*) FROM raw.taxi_zones").fetchone()[0]
            context.log.info(f"✅ Loaded {row_count} taxi zone records into raw.taxi_zones")
            
        else:
            context.log.warning(f"⚠️ Source file not found: {source_file}")
            # Create empty table with expected schema
            conn.execute("""
                CREATE OR REPLACE TABLE raw.taxi_zones (
                    locationid INTEGER,
                    borough VARCHAR,
                    zone VARCHAR,
                    service_zone VARCHAR
                )
            """)
            context.log.info("Created empty taxi_zones table with expected schema")
            
    finally:
        conn.close()

@asset(group_name="data_validation", deps=[taxi_trips_raw, taxi_zones_raw])
def raw_data_validation(context: AssetExecutionContext) -> None:
    """
    Validate the loaded raw data and log data quality metrics.
    """
    
    raw_db_path = os.getenv("DUCKDB_RAW_PATH", "/app/02_duck_db/01_raw/raw.duckdb")
    conn = connect_with_retry(raw_db_path, read_only=True)
    
    try:
        # Validate taxi_trips
        trips_count = conn.execute("SELECT COUNT(*) FROM raw.taxi_trips").fetchone()[0]
        zones_count = conn.execute("SELECT COUNT(*) FROM raw.taxi_zones").fetchone()[0]
        
        context.log.info(f"📊 Data Quality Report:")
        context.log.info(f"   - Taxi Trips: {trips_count:,} records")
        context.log.info(f"   - Taxi Zones: {zones_count:,} records")
        
        if trips_count > 0:
            # Check for nulls in key columns
            null_checks = conn.execute("""
                SELECT 
                    SUM(CASE WHEN pickup_datetime IS NULL THEN 1 ELSE 0 END) as null_pickup_datetime,
                    SUM(CASE WHEN dropoff_datetime IS NULL THEN 1 ELSE 0 END) as null_dropoff_datetime,
                    SUM(CASE WHEN trip_distance IS NULL THEN 1 ELSE 0 END) as null_trip_distance
                FROM raw.taxi_trips
            """).fetchone()
            
            context.log.info(f"   - Null pickup_datetime: {null_checks[0]}")
            context.log.info(f"   - Null dropoff_datetime: {null_checks[1]}")
            context.log.info(f"   - Null trip_distance: {null_checks[2]}")
            
        context.log.info("✅ Raw data validation completed")
        
    finally:
        conn.close()

from dagster import Definitions

defs = Definitions(
    assets=[
        taxi_trips_raw,
        taxi_zones_raw, 
        raw_data_validation
    ],
)
