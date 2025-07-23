# Base image for the Dagster service
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for Python package installations
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Dagster project code into the container
COPY . /app/03_dagster/

# Create the Dagster home directory for persistent storage
RUN mkdir -p /opt/dagster/dagster_home

# Set the DAGSTER_HOME environment variable
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Copy Dagster configuration file
COPY dagster.yaml /opt/dagster/dagster_home/

# Expose the port for the Dagster UI
EXPOSE 3000

# Start the Dagster development server with PostgreSQL configuration
CMD ["sh", "-c", "cd /app/03_dagster && dagster dev -h 0.0.0.0 -p 3000"]
