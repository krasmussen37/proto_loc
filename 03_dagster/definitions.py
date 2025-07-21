"""
Dagster definitions for proto_loc analytics platform
"""

from dagster import Definitions, asset
import duckdb
import os
from pathlib import Path


@asset
def raw_data_check():
    """Check raw data availability"""
    base_path = Path(__file__).parent.parent
    raw_db_path = os.getenv("DUCKDB_RAW_PATH", str(base_path / "02_duck_db" / "01_raw" / "raw.duckdb"))
    
    # Create empty database if it doesn't exist
    if not Path(raw_db_path).exists():
        Path(raw_db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(raw_db_path)
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.close()
    
    return {"status": "Raw database initialized"}


defs = Definitions(
    assets=[raw_data_check],
)
