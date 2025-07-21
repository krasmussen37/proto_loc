FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Dagster code
COPY . /app/03_dagster/

# Expose port
EXPOSE 3000

# Start Dagster
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
