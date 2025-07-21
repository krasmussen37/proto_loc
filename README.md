# proto_loc | Analytics-to-AI Platform

A full-stack, local-first analytics and AI platform that mirrors enterprise cloud capabilities. Built for rapid prototyping, training, and community demonstration.

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your API keys
3. Run `docker-compose up`
4. Access services:
   - Dagster: http://localhost:3000
   - Superset: http://localhost:8088
   - Jupyter: http://localhost:8888

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
├── other/               # Supporting code
└── README.md
```

## Development Phases

### Phase 1: Infrastructure Setup
Complete - All services configured and ready for data

### Phase 2: Analytics Development
In progress - NYC taxi data pipeline and dashboards

## Services

- **DuckDB**: Embedded analytical database
- **Dagster**: Data orchestration and pipeline management
- **dbt**: Data transformation framework
- **Cube**: Semantic layer and API
- **Superset**: Business intelligence and visualization
- **PandasAI**: AI-powered data analysis

## Configuration

See `.env.example` for required environment variables.

## Updating Dependencies

To update tools:
1. Check release notes for breaking changes
2. Update version in requirements.txt
3. Rebuild: `docker-compose build --no-cache`
4. Test with validation notebook
5. Run in dev environment first

## Troubleshooting

- **Database locks**: Use read-only mode for viewers; route writes through Dagster
- **Service not starting**: Check docker logs with `docker-compose logs`
- **API key issues**: Verify .env and restart services
- **Connectivity**: Run network test in validation notebook

## DuckDB Concurrency Notes

DuckDB supports single-writer/multiple-readers. Superset/Cube are read-only. For writes, use Dagster/dbt. If locks occur, consider PostgreSQL for high concurrency.

## License

MIT License - see LICENSE file for details
