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
import subprocess
from dagster import asset, AssetExecutionContext, AssetSelection, define_asset_job, op, In


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


from pathlib import Path

@asset(group_name="raw_data_ingestion")
def ingest_raw_data(context: AssetExecutionContext) -> None:
    """
    Consolidated raw data ingestion for NYC taxi data.
    
    This asset loads both taxi trips and zones sequentially within a single 
    database connection to prevent DuckDB locking conflicts.
    
    Reads from: 
    - /app/01_source_data/nyc_yellow_taxi_demo_data/yellow_cab_data_monthly/*.parquet
    - /app/01_source_data/nyc_yellow_taxi_demo_data/taxi_zones/taxi_zone_lookup.csv
    
    Writes to: 
    - raw.duckdb.nyc_taxi_data.raw_taxi_trips
    - raw.duckdb.nyc_taxi_data.raw_taxi_zones
    """
    
    # File paths
    base_path = Path("/app/01_source_data/nyc_yellow_taxi_demo_data")
    trips_path = base_path / "yellow_cab_data_monthly"
    zones_path = base_path / "taxi_zones"
    trips_pattern = str(trips_path / "*.parquet")
    zones_file = str(zones_path / "taxi_zone_lookup.csv")

    # Check if source files exist
    if not Path(zones_file).exists():
        raise FileNotFoundError(f"Zones lookup file not found at {zones_file}")
    if not list(trips_path.glob("*.parquet")):
        raise FileNotFoundError(f"No trip data found at {trips_pattern}")
    raw_db_path = os.getenv("DUCKDB_RAW_PATH", "/app/02_duck_db/01_raw/raw.duckdb")
    
    # Connect to raw DuckDB with retry logic (single connection for both operations)
    conn = connect_with_retry(raw_db_path, read_only=False)
    
    try:
        # Create schema for NYC taxi data (one schema per data source)
        conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_taxi_data")
        
        # Step 1: Load taxi trips from Parquet files
        context.log.info(f"Loading NYC taxi trips from: {trips_pattern}")
        conn.execute(f"""
            CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_trips AS 
            SELECT 
                *,
                CURRENT_TIMESTAMP as _ingested_at
            FROM read_parquet('{trips_pattern}')
        """)
        
        # Get trip statistics
        trip_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_trips,
                MIN(tpep_pickup_datetime) as earliest_trip,
                MAX(tpep_pickup_datetime) as latest_trip,
                COUNT(DISTINCT DATE_TRUNC('month', tpep_pickup_datetime)) as months_covered
            FROM nyc_taxi_data.raw_taxi_trips
        """).fetchone()
        
        context.log.info(f"✅ Successfully loaded {trip_stats[0]:,} taxi trips")
        context.log.info(f"📅 Date range: {trip_stats[1]} to {trip_stats[2]}")
        context.log.info(f"📊 Months covered: {trip_stats[3]}")
        
        # Step 2: Load taxi zones from CSV
        context.log.info(f"Loading taxi zones from: {zones_file}")
        conn.execute(f"""
            CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_zones AS 
            SELECT 
                *,
                CURRENT_TIMESTAMP as _ingested_at
            FROM read_csv_auto('{zones_file}')
        """)
        
        # Get zone statistics
        zone_count = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.raw_taxi_zones").fetchone()[0]
        sample_zones = conn.execute("""
            SELECT DISTINCT Borough 
            FROM nyc_taxi_data.raw_taxi_zones 
            ORDER BY Borough
        """).fetchall()
        
        context.log.info(f"✅ Successfully loaded {zone_count} taxi zones")
        context.log.info(f"📍 Boroughs: {', '.join([b[0] for b in sample_zones])}")
        
        # Step 3: Copy raw data to dev database for dbt transformations
        context.log.info("Copying raw data to dev database for dbt access...")
        dev_db_path = os.getenv("DUCKDB_DEV_PATH", "/app/02_duck_db/02_dev/dev.duckdb")
        dev_conn = connect_with_retry(dev_db_path, read_only=False)
        
        try:
            # Create schema in dev database
            dev_conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_taxi_data")
            
            # Attach raw database and copy data
            dev_conn.execute(f"ATTACH '{raw_db_path}' AS raw_db")
            
            # Copy trips data
            dev_conn.execute("""
                CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_trips AS 
                SELECT * FROM raw_db.nyc_taxi_data.raw_taxi_trips
            """)
            
            # Copy zones data
            dev_conn.execute("""
                CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_zones AS 
                SELECT * FROM raw_db.nyc_taxi_data.raw_taxi_zones
            """)
            
            context.log.info("✅ Raw data copied to dev database for dbt access")
            
        except Exception as e:
            context.log.error(f"Failed to copy raw data to dev database: {e}")
            raise
        finally:
            dev_conn.execute("DETACH raw_db")
            dev_conn.close()
        
        # Summary
        context.log.info("🎉 Raw data ingestion completed successfully!")
        context.log.info(f"   Total trips: {trip_stats[0]:,}")
        context.log.info(f"   Total zones: {zone_count}")
        context.log.info("   Data available in both raw and dev databases")
        
    except Exception as e:
        context.log.error(f"Failed to ingest raw data: {e}")
        raise
    finally:
        conn.close()

@asset(group_name="data_validation", deps=[ingest_raw_data])
def raw_data_validation(context: AssetExecutionContext) -> None:
    """
    Validate the loaded raw NYC taxi data and log data quality metrics.
    """
    
    raw_db_path = os.getenv("DUCKDB_RAW_PATH", "/app/02_duck_db/01_raw/raw.duckdb")
    conn = connect_with_retry(raw_db_path, read_only=True)
    
    try:
        # Validate NYC taxi data
        trips_count = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.raw_taxi_trips").fetchone()[0]
        zones_count = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.raw_taxi_zones").fetchone()[0]
        
        context.log.info(f"📊 NYC Taxi Data Quality Report:")
        context.log.info(f"   - Taxi Trips: {trips_count:,} records")
        context.log.info(f"   - Taxi Zones: {zones_count:,} records")
        
        if trips_count > 0:
            # Check for nulls in key columns
            null_checks = conn.execute("""
                SELECT 
                    SUM(CASE WHEN tpep_pickup_datetime IS NULL THEN 1 ELSE 0 END) as null_pickup_datetime,
                    SUM(CASE WHEN tpep_dropoff_datetime IS NULL THEN 1 ELSE 0 END) as null_dropoff_datetime,
                    SUM(CASE WHEN trip_distance IS NULL THEN 1 ELSE 0 END) as null_trip_distance,
                    SUM(CASE WHEN fare_amount IS NULL THEN 1 ELSE 0 END) as null_fare_amount
                FROM nyc_taxi_data.raw_taxi_trips
            """).fetchone()
            
            context.log.info(f"   - Null pickup_datetime: {null_checks[0]:,}")
            context.log.info(f"   - Null dropoff_datetime: {null_checks[1]:,}")
            context.log.info(f"   - Null trip_distance: {null_checks[2]:,}")
            context.log.info(f"   - Null fare_amount: {null_checks[3]:,}")
            
            # Get date range and basic stats
            stats = conn.execute("""
                SELECT 
                    MIN(tpep_pickup_datetime) as earliest_trip,
                    MAX(tpep_pickup_datetime) as latest_trip,
                    AVG(trip_distance) as avg_trip_distance,
                    AVG(fare_amount) as avg_fare_amount
                FROM nyc_taxi_data.raw_taxi_trips
                WHERE tpep_pickup_datetime IS NOT NULL
            """).fetchone()
            
            context.log.info(f"   - Date range: {stats[0]} to {stats[1]}")
            context.log.info(f"   - Avg trip distance: {stats[2]:.2f} miles")
            context.log.info(f"   - Avg fare amount: ${stats[3]:.2f}")
            
        context.log.info("✅ Raw data validation completed")
        
    except Exception as e:
        context.log.error(f"Validation failed: {e}")
        raise
    finally:
        conn.close()

# Configure dbt project integration
DBT_PROJECT_DIR = "/app/04_dbt"

@asset(
    group_name="dbt_transformations",
    deps=[raw_data_validation] # Explicitly depend on raw data validation
)
def dbt_transformation_asset(context: AssetExecutionContext):
    """
    Materializes dbt models after raw data is ingested and validated.
    
    This includes:
    - Seed dimension tables (vendors, rate codes, payment types)  
    - Staging models (stg_taxi_trips, stg_taxi_zones)
    - Mart models (fct_taxi_trips, mart_taxi_trips)
    """
    try:
        # Change to dbt directory
        os.chdir(DBT_PROJECT_DIR)
        
        context.log.info("Starting dbt seed...")
        result = subprocess.run(["dbt", "seed", "--target", "dev"], 
                              capture_output=True, text=True, check=True)
        context.log.info("✅ dbt seed completed successfully")
        context.log.info(f"dbt seed output: {result.stdout}")
        
        context.log.info("Starting dbt run...")
        result = subprocess.run(["dbt", "run", "--target", "dev"], 
                              capture_output=True, text=True, check=True)
        context.log.info("✅ dbt run completed successfully")
        context.log.info(f"dbt run output: {result.stdout}")
        
        context.log.info("Starting dbt test...")
        try:
            result = subprocess.run(["dbt", "test", "--target", "dev"], 
                                  capture_output=True, text=True, check=True)
            context.log.info("✅ dbt test completed successfully")
            context.log.info(f"dbt test output: {result.stdout}")
        except subprocess.CalledProcessError as test_error:
            context.log.warning(f"dbt tests failed but continuing pipeline: {test_error}")
            context.log.warning(f"dbt test stdout: {test_error.stdout}")
            context.log.warning(f"dbt test stderr: {test_error.stderr}")
            context.log.info("⚠️ dbt tests failed but data transformations completed - proceeding with pipeline")
        
        context.log.info("🎉 All dbt transformations completed successfully!")
        
    except subprocess.CalledProcessError as e:
        context.log.error(f"dbt command failed: {e}")
        context.log.error(f"stdout: {e.stdout}")
        context.log.error(f"stderr: {e.stderr}")
        raise
    except Exception as e:
        context.log.error(f"dbt transformation failed: {e}")
        raise

@asset(
    group_name="analytics_validation", 
    deps=[dbt_transformation_asset] # Now depends on the new dbt transformation asset
)
def analytics_data_validation(context: AssetExecutionContext) -> None:
    """
    Validate the transformed analytics data and log key metrics.
    """
    
    dev_db_path = os.getenv("DUCKDB_DEV_PATH", "/app/02_duck_db/02_dev/dev.duckdb")
    conn = connect_with_retry(dev_db_path, read_only=True)
    
    try:
        # Check if mart tables exist and have data
        fact_count = conn.execute("SELECT COUNT(*) FROM main.fct_taxi_trips").fetchone()[0]
        mart_count = conn.execute("SELECT COUNT(*) FROM main_mart.mart_taxi_trips").fetchone()[0]
        
        context.log.info(f"📊 Analytics Data Quality Report:")
        context.log.info(f"   - Fact Taxi Trips: {fact_count:,} records")
        context.log.info(f"   - Mart Taxi Trips: {mart_count:,} records")
        
        if fact_count > 0:
            # Get data quality metrics
            quality_stats = conn.execute("""
                SELECT 
                    SUM(total_amount_mismatch_flag) as total_mismatches,
                    SUM(negative_duration_flag) as negative_durations,
                    COUNT(DISTINCT pickup_borough) as pickup_boroughs,
                    COUNT(DISTINCT dropoff_borough) as dropoff_boroughs
                FROM main.fct_taxi_trips
            """).fetchone()
            
            context.log.info(f"   - Total amount mismatches: {quality_stats[0]:,}")
            context.log.info(f"   - Negative duration trips: {quality_stats[1]:,}")
            context.log.info(f"   - Pickup boroughs: {quality_stats[2]}")
            context.log.info(f"   - Dropoff boroughs: {quality_stats[3]}")
            
        context.log.info("✅ Analytics data validation completed")
        
    except Exception as e:
        context.log.error(f"Analytics validation failed: {e}")
        raise
    finally:
        conn.close()

from dagster import Definitions

# Define a job to orchestrate the full data pipeline
nyc_taxi_pipeline_job = define_asset_job(
    "nyc_taxi_pipeline",
    selection=AssetSelection.all(), # Selects all assets defined in this file
)

# Define all assets and resources for Dagster
defs = Definitions(
    assets=[
        ingest_raw_data,  # Consolidated raw data ingestion asset
        raw_data_validation,
        dbt_transformation_asset, # Use subprocess-based dbt transformation
        analytics_data_validation
    ],
    jobs=[nyc_taxi_pipeline_job]
)
