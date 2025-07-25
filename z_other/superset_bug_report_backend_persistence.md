# Apache Superset Bug Report: SQLLAB_BACKEND_PERSISTENCE Compatibility Issue

## Summary
When `SQLLAB_BACKEND_PERSISTENCE: True` (the default setting) is enabled, SQL Lab fails with error "'dict' object has no attribute 'set'" preventing any SQL Lab functionality. Setting to `False` resolves the issue but loses backend persistence features.

## Expected Behavior
- SQL Lab should store query tabs and state on the backend server
- Query tabs should persist across browser sessions and devices  
- Users should be able to execute queries normally in SQL Lab
- Backend persistence should work as designed in Superset 5.0.0

## Actual Behavior
- SQL Lab completely fails to execute any queries
- Error message: "DuckDB Error: 'dict' object has no attribute 'set'"
- No SQL Lab functionality available (schema browsing, query execution, table preview)
- Issue occurs immediately when trying to use any SQL Lab feature
- Error appears consistently across all database connections

## Environment Details

### Superset Configuration
- **Superset Version**: 5.0.0 (Docker image: apache/superset:5.0.0)  
- **Python Version**: 3.10.18
- **Platform**: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64 (WSL2 on Windows)

### Key Dependencies
- **duckdb**: 1.3.2
- **duckdb-engine**: 0.13.0  
- **sqlalchemy**: 1.4.54
- **PostgreSQL**: 15-alpine (metadata database)

### Database Configuration
- **Primary Database**: DuckDB 1.3.2 (file-based, read-only for Superset)
- **Metadata Database**: PostgreSQL 15-alpine (for Superset metadata)
- **Cache/Queue**: Redis 7-alpine
- **Dataset Size**: ~99M records in primary table

### Feature Flags Configuration
```python
FEATURE_FLAGS = {
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True, 
    'GLOBAL_ASYNC_QUERIES': False,
    'VERSIONED_EXPORT': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'SQLLAB_BACKEND_PERSISTENCE': True,  # PROBLEMATIC - causes 'dict' has no 'set' error
}
```

### SQLAlchemy Configuration
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://superset:superset@postgres:5432/superset'
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_timeout': 20, 
    'pool_recycle': 1800,
    'max_overflow': 0,
    'pool_pre_ping': True,
    'connect_args': {
        'connect_timeout': 10,
        'application_name': 'superset_metadata'
    }
}
```

## Steps to Reproduce
1. Set `SQLLAB_BACKEND_PERSISTENCE: True` in superset_config.py (default setting)
2. Navigate to SQL Lab in Superset UI
3. Select any database connection
4. Attempt to browse schema, preview table, or execute any query
5. Observe "'dict' object has no attribute 'set'" error
6. Confirm by setting `SQLLAB_BACKEND_PERSISTENCE: False` - issue resolves

## Error Details

### Exact Error Message
```
DuckDB Error: 'dict' object has no attribute 'set'
```

### Error Context
- **Occurs**: Immediately when trying to use any SQL Lab feature
- **Scope**: All database connections (DuckDB, PostgreSQL, Cube.js)
- **Frequency**: 100% reproducible
- **Resolution**: Only resolved by disabling backend persistence

### Affected Operations
- Schema browsing
- Table previews  
- Query execution
- Any SQL Lab interaction

## Database Connection Details

### DuckDB Connection String
```
duckdb:///app/02_duck_db/01_raw/raw.duckdb
```

### Connection Configuration
- **Engine**: duckdb-engine 0.13.0
- **Database File**: Read-only access, file-based DuckDB
- **Schema**: Standard DuckDB schema structure
- **Tables**: ~99M record taxi dataset with proper column types

## Additional Context

### Working Workaround
Setting `SQLLAB_BACKEND_PERSISTENCE: False` completely resolves the issue:
- SQL Lab functions normally
- All query operations work
- Schema browsing and table previews work
- Query execution successful

### Trade-offs with Workaround
- ❌ Query tabs stored in browser localStorage only
- ❌ No cross-device query tab persistence  
- ❌ Query tabs may be lost on browser data clearing
- ❌ Reduced collaboration capabilities

### Environment Specifics
- **Container Runtime**: Docker 27.3.1 on WSL2
- **File System**: WSL2 Windows mount (/mnt/c/...)
- **Database Storage**: Local file-based DuckDB
- **Network**: Docker Compose bridge network

## Infrastructure Configuration

### PostgreSQL Metadata Database
- **Version**: PostgreSQL 15-alpine
- **Connection**: Healthy and responsive
- **Usage**: Superset metadata only
- **Performance**: Normal operation

### DuckDB Analytics Database
- **Version**: DuckDB 1.3.2 with duckdb-engine 0.13.0
- **Access Pattern**: Read-only for Superset
- **File Location**: Container volume mount
- **Schema**: Standard nyc_taxi_data schema with proper types

## Impact
- **Severity**: High - Completely breaks SQL Lab when using default Superset 5.0.0 setting
- **Workaround**: Available but reduces functionality
- **Users Affected**: Any Superset 5.0.0 deployment with backend persistence enabled (default)

## Suspected Root Cause
The error "'dict' object has no attribute 'set'" suggests a Python object type mismatch in the backend persistence code, possibly related to:
- SQLAlchemy object serialization for backend storage
- DuckDB-specific data type handling in persistence layer
- Interaction between duckdb-engine 0.13.0 and Superset 5.0.0 persistence

## Configuration Context
This issue occurs in a Docker-based analytics platform designed for large dataset processing, where DuckDB serves as the primary analytical database with PostgreSQL handling Superset metadata.

---

**Environment**: Docker-based analytics platform with DuckDB + PostgreSQL  
**Use Case**: Analytics platform for large dataset processing (Phase 1: Infrastructure development)  
**Contact**: Available for additional debugging/testing as needed