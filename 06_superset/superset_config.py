#!/usr/bin/env python3
"""
Superset configuration for proto_loc analytics platform.

This configuration ensures Superset uses PostgreSQL for metadata persistence
and includes optimizations for the analytics platform.
"""

import os
import secrets
import base64
from flask_caching.backends.filesystemcache import FileSystemCache

# Database Configuration - Use PostgreSQL for persistence
POSTGRES_HOST = os.getenv('SUPERSET_POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('SUPERSET_POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('SUPERSET_POSTGRES_DB', 'superset')
POSTGRES_USER = os.getenv('SUPERSET_POSTGRES_USER', 'superset')
POSTGRES_PASSWORD = os.getenv('SUPERSET_POSTGRES_PASSWORD', 'superset')

# SQLAlchemy Database URI for PostgreSQL  
SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

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

# Security Configuration
# Generate a strong, random SECRET_KEY if not provided or too short
secret_key_env = os.getenv('SUPERSET_SECRET_KEY')
if not secret_key_env or len(secret_key_env) < 32:
    # Generate a 32-byte (256-bit) random key and encode it to a base64 string
    SECRET_KEY = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    print("WARNING: SUPERSET_SECRET_KEY not found or too short. Generating a random base64 key for development.")
else:
    SECRET_KEY = secret_key_env

# JWT Configuration for async queries
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds
JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days in seconds
GLOBAL_ASYNC_QUERIES_JWT_SECRET = SECRET_KEY  # Use the same secret key for JWT

# Redis Configuration for Caching - HIGH PERFORMANCE
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')

# Cache Configuration - Restore Redis for high performance
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_DB,
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
}

# Data Cache Configuration - Restore Redis for distributed caching  
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_DB,
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    'CACHE_KEY_PREFIX': 'superset_data_',
}

# Feature Flags - Restore async queries with working Redis
FEATURE_FLAGS = {
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'GLOBAL_ASYNC_QUERIES': False,  # DISABLED - breaks chart data format (forEach errors)
    'VERSIONED_EXPORT': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'SQLLAB_BACKEND_PERSISTENCE': False, # CONFIRMED ISSUE - causes 'dict' object has no attribute 'set' error
}

# CSV Export Configuration
CSV_EXPORT = {
    'encoding': 'utf-8',
}

# Disable Row Level Security - can interfere with chart rendering
ENABLE_ROW_LEVEL_SECURITY = False

# Email Configuration (optional - configure if needed)
SMTP_HOST = os.getenv('SUPERSET_SMTP_HOST', 'localhost')
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = os.getenv('SUPERSET_SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SUPERSET_SMTP_PASSWORD', '')
SMTP_MAIL_FROM = os.getenv('SUPERSET_SMTP_FROM', 'superset@example.com')

# Async Query Configuration - Restore Redis for high performance
RESULTS_BACKEND = {
    'cache_type': 'redis',
    'cache_redis_host': REDIS_HOST,
    'cache_redis_port': REDIS_PORT,
    'cache_redis_db': REDIS_DB,
}

# Celery Configuration for Superset 5.0.0
class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    worker_log_level = 'INFO'
    worker_prefetch_multiplier = 1
    task_acks_late = True
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
    }

CELERY_CONFIG = CeleryConfig

# SQL Lab Configuration
SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_TIMEOUT = 300  # 5 minutes
SUPERSET_WEBSERVER_TIMEOUT = 300

# Performance Settings
SUPERSET_WEBSERVER_PORT = 8088
SUPERSET_WORKERS = 1
SUPERSET_WORKER_CLASS = 'gthread'
SUPERSET_WORKER_CONNECTIONS = 1000
SUPERSET_WORKER_TIMEOUT = 60
SUPERSET_KEEPALIVE = 2

# Security Headers - Re-enable for proper chart rendering
TALISMAN_ENABLED = True  # Re-enabled - needed for proper AJAX requests
WTF_CSRF_ENABLED = True  # Re-enabled - might be required for chart builder

# Logging Configuration
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = 'INFO'
FILENAME = '/tmp/superset.log'

# Custom CSS (optional)
# CUSTOM_CSS = """
# .navbar-brand {
#     font-weight: bold;
# }
# """

# Override any default Redis configurations - comprehensive approach
import os
redis_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
os.environ['REDIS_URL'] = redis_url
os.environ['CACHE_REDIS_URL'] = redis_url
os.environ['CELERY_RESULT_BACKEND'] = redis_url

# Additional Redis URL configurations for Superset 5.0.0
CACHE_REDIS_URL = redis_url
REDIS_URL = redis_url

# Explicitly disable any localhost Redis fallbacks
REDIS_LOCALHOST_OVERRIDE = False

print(f"✅ Superset configured with PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
print(f"🔧 Cache backend: Redis at {REDIS_HOST}:{REDIS_PORT}")
print(f"🔧 Redis URL override: redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
print(f"⚙️  Feature flags enabled: {len(FEATURE_FLAGS)} features")
