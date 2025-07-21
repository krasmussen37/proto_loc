# proto_loc | Analytics-to-AI Platform

A full-stack, local-first analytics and AI platform that mirrors enterprise cloud capabilities. Built for rapid prototyping, training, and community demonstration.

## Phase 1: Stable and Persistent Infrastructure

This initial phase focused on building a robust and reliable platform foundation. All services are now containerized, with persistent data storage and health checks to ensure stability.

### Key Features
- **Dockerized Services**: All components (Dagster, dbt, Superset, Cube, Jupyter) run in isolated Docker containers.
- **Persistent Data**: Dagster and Superset now use named volumes to persist data across container restarts.
- **Health Checks**: Superset includes a health check to ensure it is running correctly.
- **Dependency Management**: All Python and Node.js dependencies have been resolved for a stable build.
- **Automated Testing**: A containerized test suite is available to validate the platform's stability.

## Quick Start

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/krasmussen37/proto_loc.git
    cd proto_loc
    ```
2.  **Configure Environment**:
    Copy the `.env.example` file to `.env` and add your API keys for AI services.
    ```bash
    cp .env.example .env
    ```
3.  **Launch the Platform**:
    ```bash
    docker-compose up -d
    ```
4.  **Access Services**:
    - **Dagster**: http://localhost:3000 (for data orchestration)
    - **Superset**: http://localhost:8088 (for BI and visualization)
    - **Jupyter**: http://localhost:8888 (for AI-powered analysis)
    - **Cube**: http://localhost:4000 (for the semantic layer)

## Next Steps: Phase 2 - End-to-End Pipeline Validation

The next phase will focus on implementing a simple data pipeline using NYC taxi data to validate that all services are working together seamlessly. This will involve:
- Ingesting raw data using Dagster
- Transforming the data with dbt
- Defining a semantic layer in Cube
- Visualizing the results in Superset
- Performing AI-powered analysis in Jupyter with PandasAI

## Project Structure

```
proto_loc/
├── 00_clinerules/          # Project rules and guidelines
├── 01_source_data/         # Raw source data files
├── 02_duck_db/           # DuckDB databases
│   ├── 01_raw/          # Raw ingestion layer
│   ├── 02_dev/          # Development environment
│   └── 03_prod/         # Production environment
├── 03_dagster/          # Data orchestration
├── 04_dbt/              # Data transformation
├── 05_cube_dev/         # Semantic layer
├── 06_superset/         # BI and visualization
├── 07_pandas_ai/        # AI-powered analytics
├── other/               # Supporting code and workplan
└── README.md
```

## License

MIT License - see LICENSE file for details
