#!/bin/bash
set -e

# Initialize Superset database only if it hasn't been initialized before
if [ ! -f /tmp/.superset_initialized ]; then
    echo "Initializing Superset database..."
    
    # Upgrade the database
    superset db upgrade
    
    # Create admin user (only if it doesn't exist)
    superset fab create-admin \
        --username admin \
        --firstname Superset \
        --lastname Admin \
        --email admin@superset.com \
        --password admin || true
    
    # Initialize Superset
    superset init
    
    # Mark as initialized
    touch /tmp/.superset_initialized
    echo "Superset initialization complete."
else
    echo "Superset already initialized, skipping database setup."
fi

# Start the Superset server
echo "Starting Superset server..."
exec superset run -h 0.0.0.0 -p 8088 --with-threads --reload --debugger
