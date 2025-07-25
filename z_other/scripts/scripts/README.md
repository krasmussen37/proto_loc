# Platform Utility Scripts

This directory contains utility scripts for platform management and validation.

## Scripts Overview

### `init_duckdb.py`
**Purpose**: Initialize empty DuckDB database files for the platform
**Usage**: 
```bash
python scripts/init_duckdb.py
```
**When to use**: First-time setup or when you need fresh database files

### `clear_platform_data.py`
**Purpose**: Safely remove all user-created tables from DuckDB databases
**Usage**:
```bash
python scripts/clear_platform_data.py
```
**When to use**: 
- Before end-to-end validation testing
- When you want a clean slate for new data
- **Safety**: Only removes user tables, preserves system tables

### `validate_platform.ipynb`
**Purpose**: Jupyter notebook for comprehensive platform health checks
**Usage**: Open in Jupyter Lab or VS Code
**When to use**:
- After platform setup to verify all services
- Before loading data to ensure connectivity
- Troubleshooting platform issues

## Quick Start Sequence

For first-time setup:
1. `python scripts/init_duckdb.py` - Create database files
2. `docker-compose up -d` - Start all services  
3. Open `scripts/validate_platform.ipynb` - Verify everything works
4. Begin loading your data!

For fresh start with existing platform:
1. `python scripts/clear_platform_data.py` - Clear existing data
2. Restart your data pipeline
3. Use validation notebook to verify

## Security Note
These scripts only interact with DuckDB databases and platform configuration. They do not access external services or modify Docker containers.