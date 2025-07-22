
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create superset user with home directory
RUN groupadd -r superset && useradd -r -g superset -d /home/superset -m superset

# Install Python packages with compatible versions
RUN pip install --upgrade pip && \
    pip install "marshmallow<3.19.0" && \
    pip install apache-superset==4.1.1 && \
    pip install duckdb==1.3.2 && \
    pip install duckdb-engine

# Create app directory
RUN mkdir -p /app && chown superset:superset /app
WORKDIR /app

# Copy custom configuration and entrypoint script
COPY superset_config.py /app/superset_config.py
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh && chown superset:superset /app/entrypoint.sh

# Switch to superset user
USER superset

# Set environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV FLASK_APP=superset


# Expose port
EXPOSE 8088


# Use entrypoint script
CMD ["/app/entrypoint.sh"]

