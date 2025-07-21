FROM apache/superset:4.0.2

# Switch to root to install dependencies
USER root

# Install DuckDB driver
RUN pip install duckdb==1.1.3

# Switch back to superset user
USER superset

# Copy custom configuration
COPY superset_config.py /app/superset_config.py

# Set environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

# Expose port
EXPOSE 8088

# Start Superset
CMD ["superset", "run", "-h", "0.0.0.0", "-p", "8088", "--with-threads", "--reload", "--debugger"]
