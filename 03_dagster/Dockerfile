# Base image for the Dagster service
FROM python:3.11-slim


# Set Dagster home directory
ENV DAGSTER_HOME=/opt/dagster/dagster_home


WORKDIR /app

# Install system dependencies required for Python package installations
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Create DAGSTER_HOME
RUN mkdir -p ${DAGSTER_HOME}

# Copy Dagster code
COPY . /app/


# Create the Dagster home directory for persistent storage
RUN mkdir -p /opt/dagster/dagster_home

# Set the DAGSTER_HOME environment variable
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Expose the port for the Dagster UI
EXPOSE 3000


# Start Dagster (command overridden by docker-compose.yml)
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
