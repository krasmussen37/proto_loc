# Data Integration Standards (proto_loc Analytics Platform)

## Future considerations
- [ ] DuckDB Single-Writer Pattern: When designing Dagster assets that write to the same DuckDB file, consolidate multiple write operations into a single asset rather than creating separate concurrent assets. This prevents database locking conflicts and ensures reliable data ingestion. Consider creating compound assets that handle multiple related data sources sequentially within one database connection.
- [ ]  [ OPEN ]

----
This document defines the standards and best practices for data ingestion and integration within the proto_loc analytics platform. All data integration processes should follow these guidelines to ensure consistency, reliability, and maintainability.

## Core Principles

### 1. Dagster-First Approach
- **All data ingestion** must be orchestrated through Dagster assets.
- Raw data files should never be manually imported or processed outside of Dagster.
- Each data source should have its own dedicated Dagster asset for ingestion.
- Use Dagster's dependency management to ensure proper execution order.

### 2. DuckDB as the Primary Data Store
- All ingested data lands in DuckDB databases following our three-tier architecture:
  - **Raw Layer**: `raw.duckdb` - Untouched source data.
  - **Dev Layer**: `dev.duckdb` - Development and staging transformations.
  - **Prod Layer**: `prod.duckdb` - Production-ready data models.

### 3. Schema-First Organization
- Raw data is organized by **data source** using dedicated schemas.
- Each source system (e.g., `nyc_taxi_data`, `crm_system`) gets its own schema in `raw.duckdb`.
- This prevents naming conflicts and provides clear data lineage.

### 4. DuckDB Locking Considerations
- **Understanding the Constraint**: DuckDB is an embedded database that supports multiple concurrent *readers* but only **one active writer** at any given time for a single `.duckdb` file. Attempting concurrent writes to the same database file will result in a lock error.
- **Handling Concurrent Writes in Dagster**:
    - **Sequential Materialization**: When multiple Dagster assets write to the same DuckDB database (e.g., `raw.duckdb`), ensure they are materialized sequentially. Dagster's asset dependencies can enforce this order.
    - **Consolidated Write Operations**: For raw ingestion into a single database, consider consolidating multiple raw table creations into a single Dagster asset or a single job that executes these operations sequentially. This guarantees only one write operation is active at a time.
- **Read-Only Connections**: Tools like Superset and Cube **must** connect to DuckDB databases in read-only mode to prevent them from inadvertently attempting write operations and causing file locks. Ensure SQLAlchemy connection strings include `?read_only=true` or similar parameters.

## Technical Implementation Standards

### Dagster Asset Patterns

#### Basic Asset Structure
```python
from dagster import asset
import duckdb
import os

@asset(description="Ingest [data source] into raw database")
def raw_[source]_[object](context) -> None:
    """
    Brief description of what this asset does.
    
    Reads from: [file path or source]
    Writes to: raw.duckdb.[schema].[table]
    """
    # Get database connection
    raw_db_path = os.getenv("DUCKDB_RAW_PATH")
    conn = duckdb.connect(raw_db_path)
    
    try:
        # Create schema if not exists
        conn.execute("CREATE SCHEMA IF NOT EXISTS [schema_name]")
        
        # Ingest logic here
        # Use DuckDB's file reading capabilities when possible
        
        # Log success
        context.log.info(f"Successfully loaded [object] into raw.duckdb.[schema].[table]")
        
    finally:
        conn.close()
```

#### File-Based Ingestion Pattern (Recommended)
For file-based sources (Parquet, CSV, JSON):
```python
@asset(description="Ingest NYC taxi trip data from Parquet files")
def raw_nyc_taxi_trips(context) -> None:
    """
    Ingests all yellow taxi trip Parquet files into a single table.
    
    Reads from: /app/01_source_data/nyc_yellow_taxi_demo_data/yellow_cab_data_monthly/*.parquet
    Writes to: raw.duckdb.nyc_taxi_data.raw_taxi_trips
    """
    raw_db_path = os.getenv("DUCKDB_RAW_PATH")
    conn = duckdb.connect(raw_db_path)
    
    try:
        # Create schema
        conn.execute("CREATE SCHEMA IF NOT EXISTS nyc_taxi_data")
        
        # Use DuckDB's native file reading for efficiency
        conn.execute("""
            CREATE OR REPLACE TABLE nyc_taxi_data.raw_taxi_trips AS 
            SELECT * FROM read_parquet('/app/01_source_data/nyc_yellow_taxi_demo_data/yellow_cab_data_monthly/*.parquet')
        """)
        
        # Get row count for logging
        result = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.raw_taxi_trips").fetchone()
        context.log.info(f"Successfully loaded {result[0]:,} taxi trips into raw database")
        
    finally:
        conn.close()
```

### Environment Variables and Paths

#### Required Environment Variables
- `DUCKDB_RAW_PATH`: Path to the raw DuckDB database (default: `/app/02_duck_db/01_raw/raw.duckdb`)
- `DUCKDB_DEV_PATH`: Path to the dev DuckDB database (default: `/app/02_duck_db/02_dev/dev.duckdb`)  
- `DUCKDB_PROD_PATH`: Path to the prod DuckDB database (default: `/app/02_duck_db/03_prod/prod.duckdb`)

#### Data Source Paths
- All source data files should be placed in `/app/01_source_data/`
- Organize source data by project or source system (e.g., `/app/01_source_data/nyc_yellow_taxi_demo_data/`)
- Use descriptive folder structures that mirror your schema organization

### Performance Optimization

#### Leverage DuckDB's Strengths
- **Use native file readers**: `read_parquet()`, `read_csv_auto()`, etc. instead of pandas
- **Batch processing**: Process multiple files in single SQL statements when possible
- **Columnar efficiency**: Take advantage of DuckDB's columnar storage for analytics workloads

#### Memory Management
- For large datasets, avoid loading entire datasets into memory
- Use DuckDB's streaming capabilities and lazy evaluation
- Monitor memory usage through Dagster's logging and resource monitoring

### Data Quality and Validation

#### Basic Data Validation
Every ingestion asset should include basic validation:
```python
# Example validation checks
conn.execute("""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT primary_key_column) as unique_keys,
        MIN(date_column) as min_date,
        MAX(date_column) as max_date
    FROM schema.table_name
""")
```

#### Error Handling
- Always use try/finally blocks to ensure database connections are closed
- Log meaningful error messages with context
- Use Dagster's built-in retry mechanisms for transient failures

## Naming Conventions

### Asset Naming
- Raw ingestion assets: `raw_[source]_[object]`
- Example: `raw_nyc_taxi_trips`, `raw_nyc_taxi_zones`

### Database Objects
- **Schemas**: Use descriptive names based on data source (e.g., `nyc_taxi_data`, `crm_system`)
- **Tables**: Prefix with `raw_` in the raw database (e.g., `raw_taxi_trips`, `raw_customer_data`)

### File Organization
- Group related assets in the same Python file
- Use descriptive file names (e.g., `nyc_taxi_ingestion.py`, `crm_data_ingestion.py`)

## Example: Complete Implementation

```python
# File: 03_dagster/nyc_taxi_ingestion.py
from dagster import asset
import duckdb
import os

@asset(description="Ingest NYC yellow taxi trip data from monthly Parquet files")
def raw_nyc_taxi_trips(context) -> None:
    """
    Combines all monthly yellow taxi Parquet files into a single raw table.
    
    Source: NYC TLC Yellow Taxi Trip Records
    Files: yellow_tripdata_YYYY-MM.parquet (Jan 2023 - May 2025)
    Output: raw.duckdb.nyc_taxi_data.raw_taxi_trips
    """
    raw_db_path = os.getenv("DUCKDB_RAW_PATH")
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
                MAX(tpep_pickup_datetime) as latest_trip
            FROM nyc_taxi_data.raw_taxi_trips
        """).fetchone()
        
        context.log.info(
            f"Successfully loaded {stats[0]:,} taxi trips "
            f"from {stats[1]} to {stats[2]}"
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
        
        # Validation
        zone_count = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.raw_taxi_zones").fetchone()[0]
        context.log.info(f"Successfully loaded {zone_count} taxi zones")
        
    except Exception as e:
        context.log.error(f"Failed to ingest taxi zones: {e}")
        raise
    finally:
        conn.close()
```

## Monitoring and Maintenance

### Asset Monitoring
- Use Dagster's asset materialization tracking to monitor ingestion frequency and success rates
- Set up alerts for failed ingestions
- Monitor data freshness and volume changes

### Performance Monitoring
- Track ingestion times and optimize slow assets
- Monitor DuckDB database sizes and performance
- Use Dagster's resource monitoring to track memory and CPU usage

This framework ensures that all data integration follows consistent patterns, making the platform reliable, maintainable, and scalable as new data sources are added.
