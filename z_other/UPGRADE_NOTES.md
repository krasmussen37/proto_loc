# Superset 5.0.0 Upgrade Notes

## Issues Encountered and Solutions

### 1. PostgreSQL Driver Missing
**Problem**: `ModuleNotFoundError: No module named 'psycopg2'`
**Root Cause**: Superset 5.0.0 uses virtual environment, but dependencies installed to system Python
**Solution**: Added `PYTHONPATH` environment variable to include both system and venv site-packages:
```dockerfile
ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages:/app/.venv/lib/python3.10/site-packages:$PYTHONPATH"
```

### 2. Chart Visualization Hanging/UI Freeze - PHASE 1
**Problem**: Charts would hang indefinitely while SQL Lab worked perfectly
**Initial Root Causes**: 
- Missing SQLAlchemy connection pooling caused slow metadata queries
- Redis async query system trying to connect to localhost:6379 instead of redis:6379

**Initial Solutions**:
- Added SQLAlchemy connection pooling configuration
- Disabled `GLOBAL_ASYNC_QUERIES` to prevent Redis connection issues
- Full container rebuild required to apply configuration changes

### 3. Chart Visualization Issues - PHASE 2 (FINAL RESOLUTION)
**Problem**: After initial fixes, Big Number charts worked but Table/Bar charts still hanging
**Root Cause Analysis**: Non-standard configuration settings breaking chart rendering engine
- `SQLLAB_BACKEND_PERSISTENCE = False` - **Primary culprit** breaking query result persistence needed for charts
- `ENABLE_ROW_LEVEL_SECURITY = True` - Interfering with chart SQL generation
- Disabled security headers (`TALISMAN_ENABLED = False`, `WTF_CSRF_ENABLED = False`) - Breaking AJAX requests

**Final Solutions**:
```python
# Critical fix - chart rendering depends on query result persistence
'SQLLAB_BACKEND_PERSISTENCE': True,  # Was False

# Disable query modification that interferes with charts
ENABLE_ROW_LEVEL_SECURITY = False,   # Was True

# Re-enable security headers for proper AJAX requests
TALISMAN_ENABLED = True,             # Was False
WTF_CSRF_ENABLED = True,             # Was False
```

### 4. Performance Optimization and Feature Restoration
**After charts working, restored performance features**:

#### Redis Configuration Fix
**Problem**: Redis still connecting to localhost:6379 despite configuration
**Solution**: Docker-level environment variables in docker-compose.yml:
```yaml
environment:
  - REDIS_URL=redis://redis:6379/0
  - CACHE_REDIS_URL=redis://redis:6379/0
  - CELERY_RESULT_BACKEND=redis://redis:6379/0
```

#### Feature Restoration
**Restored full performance configuration**:
```python
# Restored Redis caching for maximum performance
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_DB,
}

# Re-enabled async queries for better UI responsiveness
FEATURE_FLAGS = {
    'GLOBAL_ASYNC_QUERIES': True,  # Re-enabled after Redis fix
    'SQLLAB_BACKEND_PERSISTENCE': True,  # Critical for chart rendering
}
```

## Final Working Configuration

### Key Dockerfile Changes
```dockerfile
# Install dependencies with explicit PYTHONPATH to include system site-packages
ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages:/app/.venv/lib/python3.10/site-packages:$PYTHONPATH"

# Install PostgreSQL driver using system pip
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir psycopg2-binary==2.9.9
```

### Key docker-compose.yml Changes
```yaml
environment:
  # Override hardcoded Redis configurations in Superset 5.0.0
  - REDIS_URL=redis://redis:6379/0
  - CACHE_REDIS_URL=redis://redis:6379/0
  - CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Key superset_config.py Changes
```python
# SQLAlchemy Engine Configuration - optimize for fast metadata operations
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,           # Connection pool size
    'pool_timeout': 20,        # Timeout for getting connection from pool
    'pool_recycle': 1800,      # Recycle connections after 30 minutes
    'max_overflow': 0,         # No overflow connections
    'pool_pre_ping': True,     # Validate connections before use
    'connect_args': {
        'connect_timeout': 10,
        'application_name': 'superset_metadata'
    }
}

# Feature Flags - Fully optimized configuration
FEATURE_FLAGS = {
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'GLOBAL_ASYNC_QUERIES': True,      # Re-enabled for performance
    'VERSIONED_EXPORT': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'SQLLAB_BACKEND_PERSISTENCE': True, # CRITICAL - must be True for charts
}

# Redis Configuration - High performance caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_DB,
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
}

# Security Configuration - Required for proper chart rendering
TALISMAN_ENABLED = True      # Required for AJAX requests
WTF_CSRF_ENABLED = True      # Required for chart builder
ENABLE_ROW_LEVEL_SECURITY = False  # Interferes with chart SQL generation
```

## Performance Results - FINAL
- **SQL Lab**: 287ms for COUNT(*) on 992M records ✅
- **Big Number Charts**: Sub-second performance ✅
- **Table/Pivot Charts**: Working with async processing ✅
- **Bar/Line Charts**: Rendering properly with large datasets ✅
- **PostgreSQL metadata**: Persistent across container restarts ✅
- **DuckDB read-only connections**: Working perfectly ✅
- **Redis caching**: Restored for maximum performance ✅
- **Async queries**: Re-enabled for better UI responsiveness ✅

## Critical Lessons Learned

### Configuration Dependencies
1. **`SQLLAB_BACKEND_PERSISTENCE`** - MUST be True for chart rendering (SQL Lab works without it, charts don't)
2. **Row-level security** - Interferes with chart SQL generation
3. **Security headers** - Required for proper AJAX requests from chart builder UI

### Redis Connection Issues
- Superset 5.0.0 has hardcoded localhost Redis defaults that override config file settings
- **Solution**: Set Redis URLs at Docker environment level, not just config file level
- Both config file AND environment variables needed for full compatibility

### Performance Optimization Order
1. **Fix basic functionality first** (PostgreSQL driver, chart rendering)
2. **Then restore performance features** (Redis caching, async queries)
3. **Test incrementally** - don't enable everything at once

## Upgrade Process - COMPLETE
1. ✅ Update Dockerfile with PYTHONPATH and dependency fixes
2. ✅ Fix chart rendering with proper SQLLAB_BACKEND_PERSISTENCE and security settings
3. ✅ Add Redis environment variables to docker-compose.yml
4. ✅ Restore Redis caching configuration
5. ✅ Re-enable async queries for maximum performance
6. ✅ **Important**: Full `docker-compose build` and restart required after each major change
7. ✅ Test all chart types (Big Number, Table, Bar, etc.) with large datasets

## Final Status: COMPLETE SUCCESS ✅
**Superset 5.0.0 with full Redis caching, async queries, and chart functionality restored**
- All chart types working with 992M record dataset
- Maximum performance configuration achieved
- Production-ready analytics platform