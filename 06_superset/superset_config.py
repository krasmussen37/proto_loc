import os
from superset.config import *

# Superset 4.0.2 configuration
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your-secret-key-here-change-me-in-production')

# Database configuration for Superset metadata
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db'

# Security settings for Superset 4.0.2
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 7  # 7 days

# Feature flags for Superset 4.0.2
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
    "DRILL_TO_DETAIL": True,
    "DRILL_BY": True,
}

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
}

# Results backend cache
RESULTS_BACKEND = None

# Async query configuration
SQLLAB_ASYNC_TIME_LIMIT_SEC = 60 * 60 * 6  # 6 hours

# Row limit for SQL Lab
DEFAULT_SQLLAB_LIMIT = 5000
SUPERSET_WORKERS = 2
SUPERSET_WORKER_TIMEOUT = 60

# Security configuration
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    "force_https": False,
    "force_https_permanent": False,
}

# CORS configuration (if needed for API access)
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']
}

# Public role permissions (customize as needed)
PUBLIC_ROLE_LIKE = "Gamma"

# DuckDB database connections will be configured through the UI
# The databases are accessible at the paths defined in environment variables
DUCKDB_DATABASES = {
    'raw': os.environ.get('DUCKDB_RAW_PATH', '/app/02_duck_db/01_raw/raw.duckdb'),
    'dev': os.environ.get('DUCKDB_DEV_PATH', '/app/02_duck_db/02_dev/dev.duckdb'),
    'prod': os.environ.get('DUCKDB_PROD_PATH', '/app/02_duck_db/03_prod/prod.duckdb')
}
