# Data Visualization Guidelines (proto_loc Analytics Platform)

This document outlines the standards and best practices for implementing data visualization and business intelligence capabilities within the proto_loc platform, specifically focusing on Apache Superset integration with DuckDB.

## Overview

The proto_loc platform uses **Apache Superset** as the primary Business Intelligence (BI) tool for creating interactive dashboards, charts, and data exploration interfaces. Superset connects to our multi-environment DuckDB setup to provide visualization capabilities across raw, development, and production data layers.

## Apache Superset Configuration

### Service Details
- **Container Service**: `superset` in docker-compose.yml
- **Default Port**: 8088 (http://localhost:8088)
- **Default Credentials**: admin / admin
- **Docker Image**: apache/superset:4.0.2
- **Persistent Storage**: Named volume `superset_data` for dashboards and metadata

### Core Dependencies
- **DuckDB Driver**: `duckdb==1.1.3`
- **SQLAlchemy Engine**: `duckdb_engine` for database connectivity
- **Container Permissions**: Runs as root user to access host-mounted DuckDB files

## DuckDB Database Connection Standards

### Critical Configuration: Read-Only Connections

**Rule**: All Superset connections to DuckDB databases MUST use read-only configuration to prevent database locking conflicts with other services (Dagster, dbt).

### Connection Configuration Template

For each DuckDB database connection in Superset:

1. **Basic Connection Settings**:
   - **SQLAlchemy URI**: `duckdb:////app/02_duck_db/[environment]/[database].duckdb`
   - **Examples**:
     - Raw: `duckdb:////app/02_duck_db/01_raw/raw.duckdb`
     - Dev: `duckdb:////app/02_duck_db/02_dev/dev.duckdb`
     - Prod: `duckdb:////app/02_duck_db/03_prod/prod.duckdb`

2. **Required Engine Parameters** (Advanced Tab):
   ```json
   {
       "connect_args": {
           "read_only": true
       }
   }
   ```

### Why Read-Only Configuration is Essential

**DuckDB Concurrency Model**: DuckDB follows a single-writer/multiple-reader pattern. Without read-only connections:
- Superset may acquire write locks preventing other services from accessing the database
- Database locking conflicts can cause service failures or data pipeline interruptions
- Multiple services attempting to write simultaneously can corrupt data

**Benefits of Read-Only BI Connections**:
- ✅ **Concurrent Access**: Multiple services can read from the same DuckDB file simultaneously
- ✅ **Data Safety**: Prevents accidental data modifications through BI interface
- ✅ **Service Stability**: Eliminates locking conflicts between Dagster, dbt, and Superset
- ✅ **Performance**: Read-only connections have lower overhead and better caching

## Database Environment Strategy

### Three-Environment Setup

**Raw Database** (`proto_loc_raw`):
- **Purpose**: Immutable source data as ingested by Dagster
- **Schema**: Source-specific schemas (e.g., `crm`, `erp`, `api_data`)
- **Access Pattern**: Read-only for all services, written only by Dagster ingestion
- **Superset Usage**: Data exploration, source data validation, lineage verification

**Development Database** (`proto_loc_dev`):
- **Purpose**: Development and testing of data transformations
- **Schemas**: `stg` (staging models), `mart` (data marts)
- **Access Pattern**: Read-write for dbt development, read-only for Superset
- **Superset Usage**: Model validation, iterative dashboard development, data quality testing

**Production Database** (`proto_loc_prod`):
- **Purpose**: Production-ready data marts for end-user consumption
- **Schemas**: `stg` (staging models), `mart` (final data marts)
- **Access Pattern**: Read-write for approved dbt releases, read-only for Superset
- **Superset Usage**: Production dashboards, executive reporting, public-facing analytics

## Dashboard Development Best Practices

### Development Workflow

1. **Data Exploration**: Use SQL Lab against `proto_loc_raw` to understand source data structure and quality
2. **Model Testing**: Connect to `proto_loc_dev` to validate dbt transformations and test chart configurations
3. **Production Deployment**: Connect to `proto_loc_prod` for final dashboard publication

### Performance Considerations

- **Materialized Tables**: Prefer connecting to dbt mart tables (materialized) over views for dashboard performance
- **Data Freshness**: Document data refresh schedules for each database environment
- **Query Optimization**: Use Superset's query optimization features and result caching

## SQL Lab Usage Guidelines

### Standard Operations
- **Data Exploration**: Query any connected database with read-only access
- **Chart Prototyping**: Test queries before creating visualizations
- **Data Quality Validation**: Verify transformation results and data integrity

### Write Operations (Special Cases)
When write operations are needed in SQL Lab:

**Option 1: Service Coordination** (Recommended)
- Temporarily stop conflicting services: `docker-compose stop dagster dbt`
- Perform write operations in SQL Lab
- Restart services: `docker-compose start dagster dbt`

**Option 2: Dedicated Write Connection** (Advanced Users)
- Create a temporary database connection without `read_only: true`
- Use only for specific write tasks
- Remove or disable connection after use

## Security and Access Management

### Default Configuration
- **Single User Setup**: Default admin/admin credentials for development
- **No Authentication**: Suitable for local development environments only

### Production Considerations (Future)
- **User Authentication**: Configure LDAP, OAuth, or database authentication
- **Role-Based Access**: Define roles for analysts, developers, and executives  
- **Database Permissions**: Implement granular access control per database/schema
- **SSL/TLS**: Enable encrypted connections for production deployments

## Integration with Other Platform Components

### Dagster Integration
- Superset consumes data produced by Dagster ingestion pipelines
- Dagster materialization schedules determine data freshness in dashboards
- Consider adding Superset dashboard refresh automation triggered by Dagster runs

### dbt Integration  
- Superset visualizes the output of dbt transformations
- dbt model documentation can be referenced in dashboard descriptions
- dbt tests validate data quality before visualization

### Jupyter Integration
- Use Jupyter for advanced analytics and AI-powered insights
- Export Jupyter findings to dashboards for broader consumption
- PandasAI queries can inform dashboard requirements and KPI selection

## Troubleshooting Common Issues

### Database Connection Failures

**Error: "Cannot open file: Read-only file system"**
- **Cause**: Missing `read_only: true` in connect_args or Docker volume permission issues
- **Solution**: Verify connect_args configuration and Docker container permissions

**Error: "Database is locked"**
- **Cause**: Another service has a write lock on the DuckDB file
- **Solution**: Ensure all Superset connections use `read_only: true` configuration

**Error: "Table does not exist"**  
- **Cause**: Querying wrong database environment or schema
- **Solution**: Verify connection targets correct database and schema exists

### Performance Issues

**Slow Dashboard Loading**
- **Cause**: Complex queries against large unmaterialized views
- **Solution**: Use dbt to materialize intermediate results as tables

**Connection Timeouts**
- **Cause**: Long-running queries blocking database access
- **Solution**: Optimize queries, add appropriate filters and limits

## Monitoring and Maintenance

### Health Checks
- Superset includes automated health checks via Docker compose
- Monitor logs: `docker-compose logs superset`
- Verify database connections in Superset UI regularly

### Data Governance
- Document all dashboard data sources and refresh schedules
- Maintain dashboard inventory with business owners and refresh frequencies
- Implement data lineage documentation linking dashboards to source systems

### Backup and Recovery
- Superset metadata stored in persistent Docker volume `superset_data`
- Export dashboard configurations for version control
- Document connection configurations for disaster recovery

## Migration and Upgrades

### Version Management
- Pin Superset version in docker-compose.yml for stability
- Test upgrades in development environment before production
- Monitor Apache Superset release notes for security patches

### Configuration Export/Import
- Export dashboard and connection configurations before major changes
- Use Superset's import/export functionality for environment promotion
- Document custom configurations and extensions for reproducibility

---

By following these guidelines, the proto_loc platform ensures reliable, performant, and scalable data visualization capabilities while maintaining data integrity and service stability across the entire analytics pipeline.
