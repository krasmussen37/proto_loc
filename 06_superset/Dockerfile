# Base image for the Superset service
FROM apache/superset:4.0.2

# Switch to root to install dependencies
USER root

# Install the DuckDB driver for connecting to DuckDB databases
RUN pip install duckdb==1.1.3

# Create the Superset home directory for persistent storage and set permissions
RUN mkdir -p /app/superset_home && \
    chown -R superset:superset /app/superset_home

# Switch back to the superset user
USER superset

# Copy the custom Superset configuration file
COPY superset_config.py /app/superset_config.py

# Set environment variables for Superset configuration and home directory
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV SUPERSET_HOME=/app/superset_home

# Expose the port for the Superset UI
EXPOSE 8088

# Initialize the Superset database, create an admin user, and start the server
CMD ["sh", "-c", "superset db upgrade && superset fab create-admin --username admin --firstname Admin --lastname User --email admin@admin.com --password admin && superset init && superset run -h 0.0.0.0 -p 8088 --with-threads --reload --debugger"]
