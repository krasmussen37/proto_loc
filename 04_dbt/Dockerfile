FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dbt and dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dbt project
COPY . /app/04_dbt/

# Set working directory
WORKDIR /app/04_dbt

# Default command
CMD ["tail", "-f", "/dev/null"]
