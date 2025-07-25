# Claude AI Memory - Phase 1: Infrastructure Development

## Phase 1 Mission
Build a **stable, forkable analytics platform** with zero proprietary data that others can quickly spin up and customize for their own use.

## Infrastructure Components & Status

### 🟢 Core Services (Stable)
- **DuckDB**: File-based OLAP database (v1.1.3)
- **Dagster**: Orchestration platform (v1.9.1)
- **dbt**: SQL transformations (v1.8.8)
- **Docker Compose**: Container orchestration

### 🟡 Needs Hardening
- **Apache Superset**: v5.0.0 (upgraded from 4.0.2, needs config cleanup)
- **Cube.js**: Semantic layer (auto-schema working, needs cleanup)
- **PandasAI**: Jupyter notebooks (minimal setup)

### 🔴 Infrastructure Development Rules

#### Before ANY Infrastructure Change:
1. **Impact Analysis**
   - How will this affect someone who forked 6 months ago?
   - Does this break backward compatibility?
   - Is there a migration path?

2. **Documentation Requirements**
   - Update `README.md` immediately
   - Add to `golden_versions.md` if version changes
   - Document in `other/Workplan.md` if significant

3. **Testing Protocol**
   - Full platform restart: `docker-compose down && docker-compose up -d`
   - Verify all services healthy: `docker-compose ps`
   - Test data flow: source → raw → staging → marts
   - Confirm UI access for all tools

## Configuration Best Practices

### Docker Compose
```yaml
# GOOD: Use environment variables for flexibility
ports:
  - "${DAGSTER_PORT:-3000}:3000"

# BAD: Hardcoded values
ports:
  - "3000:3000"
```

### Service Dependencies
```yaml
# GOOD: Explicit health checks
depends_on:
  postgres:
    condition: service_healthy

# BAD: Simple depends_on
depends_on:
  - postgres
```

### Volume Management
```yaml
# GOOD: Named volumes for persistence
volumes:
  - postgres_data:/var/lib/postgresql/data

# BAD: Anonymous volumes
volumes:
  - /var/lib/postgresql/data
```

## Common Infrastructure Tasks

### Adding a New Service
1. Check `golden_versions.md` for approved versions
2. Add to `docker-compose.yml` with:
   - Health checks
   - Configurable ports
   - Proper volume mounts
   - Network assignment
3. Update `README.md` with access instructions
4. Test full platform startup

### Upgrading a Service Version
1. **NEVER** downgrade to fix issues
2. Test in isolated environment first
3. Check breaking changes in release notes
4. Update `golden_versions.md`
5. Provide migration instructions

### Modifying Core Configurations
1. Identify configuration type:
   - Runtime (environment variables) ✅
   - Build-time (Dockerfile) ⚠️
   - Static (config files) 🔴
2. Prefer runtime configuration
3. Document all non-obvious settings

## Service-Specific Guidelines

### Dagster Configuration
- Keep `dagster.yaml` minimal
- Use environment variables for paths
- Sequential execution for DuckDB writes
- Avoid complex scheduling in Phase 1

### dbt Configuration
- `profiles.yml` uses environment variables
- Three targets: dev, test, prod
- No incremental models in Phase 1
- Simple folder structure

### Superset Configuration
- Read-only database connections only
- Use SQLAlchemy URIs with `?mode=ro`
- Export dashboards as JSON for version control
- Minimal custom CSS/themes

### Cube.js Configuration
- Auto-schema generation enabled
- Minimal `cube.js` config file
- PostgreSQL-compatible SQL interface
- No custom pre-aggregations in Phase 1

## Anti-Patterns to Avoid

### ❌ Over-Engineering
```python
# BAD: Complex abstractions for simple tasks
class AbstractDataLoaderFactoryBuilder:
    ...

# GOOD: Direct, clear implementation
def load_taxi_data(file_path):
    return pd.read_parquet(file_path)
```

### ❌ Hardcoded Paths
```python
# BAD
DB_PATH = "/home/user/proto_loc/02_duck_db/dev.duckdb"

# GOOD
DB_PATH = os.environ.get("DUCKDB_DEV_PATH", "/app/02_duck_db/02_dev/dev.duckdb")
```

### ❌ Version Proliferation
```dockerfile
# BAD: Different Python versions everywhere
FROM python:3.9  # Dagster
FROM python:3.11 # dbt
FROM python:3.8  # Superset

# GOOD: Consistent versions
FROM python:3.11 # All services
```

## Infrastructure Validation Checklist

Before considering Phase 1 complete:

- [ ] All services start with `docker-compose up -d`
- [ ] No errors in any service logs
- [ ] Sample data loads successfully
- [ ] Can create chart in Superset from dbt mart
- [ ] Cube.js shows available cubes
- [ ] README has clear setup instructions
- [ ] No hardcoded paths or credentials
- [ ] Configuration uses environment variables
- [ ] Services restart cleanly
- [ ] Fork and setup takes < 30 minutes

## Troubleshooting Patterns

### Service Won't Start
1. Check logs: `docker-compose logs [service]`
2. Verify dependencies are healthy
3. Check port conflicts
4. Validate environment variables

### Database Connection Issues
1. Confirm DuckDB file permissions
2. Check mount paths in docker-compose
3. Verify read-only mode for BI tools
4. Test with simple query first

### Version Conflicts
1. Check `golden_versions.md`
2. Review Dockerfile base images
3. Inspect package lock files
4. Ensure consistent Python version

## Next Steps for Phase 1 Completion
1. Finalize Superset 5.0.0 configuration
2. Clean up test schemas in Cube.js
3. Document all environment variables
4. Create setup validation script
5. Test fresh fork scenario