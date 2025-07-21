import os

# Superset configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'proto_loc-secret-key-change-in-production')

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset/superset.db'

# Enable DuckDB support
ENABLE_DUCKDB = True

# Security settings
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 7  # 7 days

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
}

# DuckDB configuration
DUCKDB_DATABASES = {
    'raw': os.environ.get('DUCKDB_RAW_PATH', '/app/02_duck_db/01_raw/raw.duckdb'),
    'dev': os.environ.get('DUCKDB_DEV_PATH', '/app/02_duck_db/02_dev/dev.duckdb'),
    'prod': os.environ.get('DUCKDB_PROD_PATH', '/app/02_duck_db/03_prod/prod.duckdb')
}
