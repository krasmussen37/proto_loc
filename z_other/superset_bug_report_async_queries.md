# Apache Superset Bug Report: GLOBAL_ASYNC_QUERIES Chart Compatibility Issue

## Summary
When `GLOBAL_ASYNC_QUERIES: True` is enabled, chart visualizations fail with JavaScript error "Cannot read properties of undefined (reading 'forEach')" while SQL Lab queries work correctly. This indicates a data format incompatibility between async query results and chart rendering.

## Expected Behavior
- Charts should render normally with async query execution
- Users should see progress indicators during query execution
- Charts should receive properly formatted data from async queries

## Actual Behavior
- Charts fail to render with "Cannot read properties of undefined (reading 'forEach')" error
- SQL Lab queries work correctly with async execution
- Error affects all chart types (Big Number, Pivot Table, etc.)
- Error occurs across different data sources (DuckDB raw tables, Cube.js semantic layer)

## Environment Details

### Superset Configuration
- **Superset Version**: 5.0.0 (Docker image: apache/superset:5.0.0)
- **Python Version**: 3.10.18
- **Platform**: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64 (WSL2 on Windows)

### Key Dependencies
- **duckdb**: 1.3.2
- **duckdb-engine**: 0.13.0
- **redis**: 4.6.0
- **celery**: 5.4.0

### Database Configuration
- **Primary Database**: DuckDB 1.3.2 (file-based, read-only for Superset)
- **Metadata Database**: PostgreSQL 15-alpine
- **Cache/Queue**: Redis 7-alpine
- **Dataset Size**: ~99M records in primary table

### Feature Flags Configuration
```python
FEATURE_FLAGS = {
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'GLOBAL_ASYNC_QUERIES': True,  # PROBLEMATIC
    'VERSIONED_EXPORT': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'SQLLAB_BACKEND_PERSISTENCE': False,  # Separate compatibility issue
}
```

### Infrastructure
- **Deployment**: Docker Compose
- **Cache**: Redis with proper configuration
- **Celery Workers**: Configured with Redis backend
- **JWT**: Properly configured for async queries

## Steps to Reproduce
1. Enable `GLOBAL_ASYNC_QUERIES: True` in superset_config.py
2. Create any chart (Big Number, Pivot Table, etc.) using a data source
3. Attempt to view the chart
4. Observe JavaScript error in browser console
5. Compare with SQL Lab query using same data source (works correctly)

## Additional Context

### Working SQL Lab Examples
These queries work correctly with async execution:
```sql
SELECT COUNT(*) as record_count FROM raw_taxi_trips LIMIT 1000;
SELECT pickup_datetime, total_amount FROM raw_taxi_trips LIMIT 10;
SELECT 
  DATE_TRUNC('month', pickup_datetime) as month,
  COUNT(*) as trip_count,
  AVG(total_amount) as avg_amount
FROM raw_taxi_trips 
GROUP BY DATE_TRUNC('month', pickup_datetime)
LIMIT 20;
```

### Error Details
- **Browser Console Error**: "Data error: Cannot read properties of undefined (reading 'forEach')"
- **Affects**: All chart types across all data sources
- **Does Not Affect**: SQL Lab query execution
- **Workaround**: Disable `GLOBAL_ASYNC_QUERIES` (impacts performance for large datasets)

## Infrastructure Details
- **Container Orchestration**: Docker Compose
- **Network**: Custom bridge network
- **Volumes**: Persistent for databases, ephemeral for application code
- **Resource Allocation**: Standard Docker defaults

## Related Configuration
The async query infrastructure appears correctly configured:
- Redis backend available and responsive
- Celery workers configured
- JWT secrets properly set
- Results backend configured for Redis
- No error messages in container logs

## Impact
- **Severity**: High - Breaks all chart visualizations when performance feature is enabled
- **Workaround**: Disable async queries (performance impact on large datasets)
- **Users Affected**: Anyone enabling async queries for performance benefits

## Suspected Root Cause
Async query execution returns data in a different JSON structure than synchronous queries, causing frontend chart components to fail when trying to iterate over undefined arrays/objects.

---

**Environment**: Docker-based analytics platform with DuckDB as primary analytical database  
**Use Case**: Analytics platform for large dataset processing (Phase 1: Infrastructure development)  
**Contact**: Available for additional debugging/testing as needed