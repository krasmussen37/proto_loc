#!/usr/bin/env python3
"""
Clear Platform Data Script

This script safely removes all existing tables from the DuckDB databases
to provide a clean starting point for end-to-end validation.

SAFETY: This script only removes user-created tables and schemas,
never touching DuckDB's internal system tables (information_schema, pg_catalog).

Usage: python clear_platform_data.py
"""

import duckdb
import os
import sys
from pathlib import Path

def clear_duckdb_tables(db_path: str, db_name: str) -> None:
    """Clear all user tables from a DuckDB database, preserving system tables."""
    if not os.path.exists(db_path):
        print(f"📂 {db_name}: Database file not found at {db_path}")
        return
    
    try:
        print(f"🧹 Clearing {db_name} database: {db_path}")
        
        with duckdb.connect(db_path) as conn:
            # Get all USER schemas (excluding system schemas)
            schemas_result = conn.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            """).fetchall()
            
            if not schemas_result:
                print(f"   ✅ {db_name}: No user schemas found - already clean")
                return
            
            # For each user schema, get all tables and drop them
            tables_dropped = 0
            for (schema_name,) in schemas_result:
                tables_result = conn.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema_name}'
                """).fetchall()
                
                for (table_name,) in tables_result:
                    full_table_name = f"{schema_name}.{table_name}"
                    conn.execute(f"DROP TABLE IF EXISTS {full_table_name}")
                    print(f"   🗑️  Dropped table: {full_table_name}")
                    tables_dropped += 1
                
                # Drop the schema if it's empty and not 'main'
                if schema_name != 'main':
                    try:
                        conn.execute(f"DROP SCHEMA IF EXISTS {schema_name}")
                        print(f"   🗑️  Dropped schema: {schema_name}")
                    except Exception as e:
                        print(f"   ⚠️  Could not drop schema {schema_name}: {e}")
            
            print(f"   ✅ {db_name}: Cleared {tables_dropped} tables")
            
    except Exception as e:
        print(f"   ❌ Error clearing {db_name}: {e}")
        return

def main():
    """Main function to clear all DuckDB databases."""
    print("🚀 Proto_loc Platform Data Clearing Script")
    print("=" * 50)
    print("🔒 SAFETY: Only user tables will be removed, system tables preserved")
    print("")
    
    # Define database paths
    db_paths = {
        "Raw Database": "02_duck_db/01_raw/raw.duckdb",
        "Dev Database": "02_duck_db/02_dev/dev.duckdb", 
        "Prod Database": "02_duck_db/03_prod/prod.duckdb"
    }
    
    # Check if we're in the right directory
    if not os.path.exists("docker-compose.yml"):
        print("❌ Error: This script must be run from the proto_loc root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    # Show what will be cleared
    print("This will safely remove user tables from:")
    for name, path in db_paths.items():
        status = "✅ Found" if os.path.exists(path) else "⚠️ Not found"
        print(f"  • {name}: {path} ({status})")
    
    print("\n🔒 System tables (information_schema, pg_catalog) will be preserved")
    print("⚠️  User data will be permanently deleted!")
    response = input("\nProceed with clearing user data? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("❌ Operation cancelled by user")
        sys.exit(0)
    
    print("\n🧹 Starting safe database cleanup...")
    
    # Clear each database
    total_cleared = 0
    for name, path in db_paths.items():
        clear_duckdb_tables(path, name)
        total_cleared += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Platform data clearing complete!")
    print(f"📊 Processed {total_cleared} databases")
    print("🔒 DuckDB system integrity preserved")
    print("🚀 Ready for fresh data ingestion")

if __name__ == "__main__":
    main()
