FROM python:3.11-slim

# Set Dagster home directory
ENV DAGSTER_HOME=/opt/dagster/dagster_home

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create DAGSTER_HOME
RUN mkdir -p ${DAGSTER_HOME}

# Copy Dagster code
COPY . /app/

# Expose port
EXPOSE 3000

# Start Dagster (command overridden by docker-compose.yml)
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
