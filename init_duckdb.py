#!/usr/bin/env python3
"""
Initialize empty DuckDB databases for proto_loc platform
"""

import duckdb
import os
from pathlib import Path

# Define database paths
base_path = Path(__file__).parent
db_paths = [
    base_path / "02_duck_db" / "01_raw" / "raw.duckdb",
    base_path / "02_duck_db" / "02_dev" / "dev.duckdb",
    base_path / "02_duck_db" / "03_prod" / "prod.duckdb"
]

def create_database(db_path: Path):
    """Create an empty DuckDB database at the specified path."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to create the database file
    conn = duckdb.connect(str(db_path))
    
    # Install essential extensions
    conn.execute("INSTALL spatial")
    conn.execute("LOAD spatial")
    print("  - Loaded spatial extension for geospatial analysis")
    
    # Create basic schemas
    if "raw" in str(db_path):
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
    else:
        conn.execute("CREATE SCHEMA IF NOT EXISTS stg")
        conn.execute("CREATE SCHEMA IF NOT EXISTS mart")
    
    conn.close()
    print(f"✓ Created database: {db_path}")

def main():
    """Initialize all DuckDB databases."""
    print("Initializing DuckDB databases...")
    
    for db_path in db_paths:
        create_database(db_path)
    
    print("\n✓ All DuckDB databases initialized successfully!")
    print("\nDatabase locations:")
    for db_path in db_paths:
        print(f"  - {db_path}")

if __name__ == "__main__":
    main()
