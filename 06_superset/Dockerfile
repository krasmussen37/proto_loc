
# Minimal Superset 4.0.2 with DuckDB support and admin user initialization
FROM apache/superset:5.0.0

# Switch to root to install DuckDB driver and setup initialization
USER root

# Install dependencies with explicit PYTHONPATH to include system site-packages
ENV PYTHONPATH="/usr/local/lib/python3.10/site-packages:/app/.venv/lib/python3.10/site-packages:$PYTHONPATH"

# Install PostgreSQL driver using system pip (since that works)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir psycopg2-binary==2.9.9

# Install Python dependencies from requirements.txt
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

# Install advanced analytics libraries (DuckDB engine version controlled by requirements.txt)
RUN pip install --no-cache-dir statsmodels scikit-learn

# Copy Superset configuration file
COPY superset_config.py /app/pythonpath/superset_config.py

# Set Superset configuration
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py
ENV PYTHONPATH=/app/pythonpath:$PYTHONPATH

# Create initialization script for admin user setup
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Initializing Superset..."\n\
\n\
# Initialize the database\n\
superset db upgrade\n\
\n\
# Create admin user if it does not exist\n\
superset fab create-admin \\\n\
    --username admin \\\n\
    --firstname Admin \\\n\
    --lastname User \\\n\
    --email admin@example.com \\\n\
    --password admin || echo "Admin user already exists or creation failed - continuing..."\n\
\n\
# Initialize roles and permissions\n\
superset init\n\
\n\
echo "Superset initialization complete. Starting server..."\n\
\n\
# Start Superset server\n\
exec gunicorn --bind 0.0.0.0:8088 --access-logfile - --error-logfile - --workers 1 --worker-class gthread --threads 20 --timeout 60 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --preload "superset.app:create_app()"\n\
' > /app/init-superset.sh && chmod +x /app/init-superset.sh

# Keep running as root for file permissions in development
# USER superset  # Commented out to allow access to mounted DuckDB files

# Expose port
EXPOSE 8088


# Use the initialization script we created
CMD ["/app/init-superset.sh"]
