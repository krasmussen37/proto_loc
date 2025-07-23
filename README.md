# proto_loc | Analytics-to-AI Platform

A full-stack, local-first analytics and AI platform that mirrors enterprise cloud capabilities. Built for rapid prototyping, training, and community demonstration.

### Setup Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/krasmussen37/proto_loc.git
   cd proto_loc
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see Configuration section below)
   ```

3. **Initialize databases**
   ```bash
   python init_duckdb.py
   ```

4. **Start all services**
   ```bash
   docker-compose up -d
   ```

5. **Initialize Production Data (Required for Cube.js)**
   Run dbt to build the initial data models in the production DuckDB. This step is crucial for Cube.js to find a schema.
   ```bash
   docker-compose exec dbt dbt run --target prod
   ```

6. **Verify services are running**
   ```bash
   docker-compose ps
   ```

## 🌐 Service Access

| Service      | URL                   | Purpose                                  | Default Credentials |
| ------------ | --------------------- | ---------------------------------------- | ------------------- |
| **Dagster**  | http://localhost:3000 | Data orchestration & pipeline management | None required       |
| **Superset** | http://localhost:8088 | BI dashboards & visualization            | admin / admin       |
| **Jupyter**  | http://localhost:8888 | Interactive notebooks & PandasAI         | Token in logs       |
| **Cube**     | http://localhost:4000 | Semantic layer API                       | None required       |

### Getting Jupyter Token
```bash
docker-compose logs jupyter | grep "token="
```

## 🧪 Testing Your Setup

### Service Health Check
Run this command to verify all services are operational:
```bash
docker-compose ps
```
**Expected Result**: All services should show "Up" status

### Individual Service Tests

1. **Dagster** (http://localhost:3000)
   - ✅ Dagster UI loads
   - ✅ Shows clean interface (no placeholder assets)
   - ✅ Ready for Phase 2 data pipeline development

2. **Superset** (http://localhost:8088)
   - ✅ Login with admin/admin
   - ✅ Can access "Databases" section
   - ✅ Follow database connection steps below

3. **Jupyter** (http://localhost:8888)
   - ✅ Notebook interface loads
   - ✅ Can create new Python notebook
   - ✅ Run test query (see instructions below)

4. **Cube** (http://localhost:4000)
   - ✅ Cube Dev Server interface loads
   - ✅ Shows DuckDB connection status
   - ✅ Schema browser operational

## 📁 Project Structure

```
proto_loc/
├── 00_clinerules/          # Project rules and guidelines
├── 01_source_data/         # Raw source data files (place CSV/JSON here)
├── 02_duck_db/           # DuckDB databases (auto-created)
│   ├── 01_raw/          # Raw ingestion layer
│   ├── 02_dev/          # Development environment  
│   └── 03_prod/         # Production environment
├── 03_dagster/          # Data orchestration
├── 04_dbt/              # Data transformation (SQL models)
├── 05_cube_dev/         # Semantic layer (metrics & dimensions)
├── 06_superset/         # BI and visualization
├── 07_pandas_ai/        # AI-powered analytics (notebooks)
├── other/               # Supporting code and utilities
└── README.md
```

## ⚙️ Configuration


| Service | URL | Default Login | Purpose |
|---------|-----|---------------|---------|
| **Superset** | http://localhost:8088 | admin / admin | BI & Dashboards |
| **Dagster** | http://localhost:3000 | No login required | Data Orchestration |
| **Jupyter** | http://localhost:8888 | Token-based (see logs) | AI-Powered Analysis |
| **PostgreSQL** | Internal (port 5432) | superset / superset | Application Metadata Store |
| **Cube** | http://localhost:4000 | Currently disabled | Semantic Layer |

### Environment Variables (.env)
Copy `.env.example` to `.env` and configure:

```bash
# AI/LLM API Keys (required for PandasAI)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here
GROQ_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
XAI_GROK_API_KEY=your-key-here

# Optional: Superset Admin Credentials
SUPERSET_ADMIN_USERNAME=admin
SUPERSET_ADMIN_PASSWORD=admin
```

**Note**: AI features require at least one API key. All other services work without API keys.

### Service Configuration Files
- **Dagster**: `03_dagster/definitions.py` - Pipeline definitions
- **dbt**: `04_dbt/profiles.yml` - Database connections
- **Cube**: `05_cube_dev/cube.js` - Schema definitions
- **Superset**: `06_superset/superset_config.py` - BI configuration

## 🏗️ Architecture & Services

### Core Components
| Component | Technology | Purpose | Port |
|-----------|------------|---------|------|
| **Database** | DuckDB | Embedded OLAP database | - |
| **Orchestration** | Dagster | Data pipeline management | 3000 |
| **Transformation** | dbt | SQL-based data modeling | - |
| **Semantic Layer** | Cube | Metrics & API layer | 4000 |
| **Visualization** | Superset | BI dashboards | 8088 |
| **AI Analysis** | Jupyter + PandasAI | Interactive AI-powered analytics | 8888 |

### Development Phases
✅ **Phase 1**: Infrastructure Setup - **COMPLETE** (Platform Stable v1.3.41)  
🔄 **Phase 2**: Data Pipeline Development - **READY TO START**

### Current Platform Status
🎯 **STABLE & OPERATIONAL** - All services running with latest compatible versions:
- **DuckDB**: v1.3.2 (latest analytical engine)
- **Dagster**: v1.11.2 (with webserver)
- **Superset**: v4.1.1 (latest BI platform) 
- **Cube**: v1.3.41 (semantic layer)
- **dbt**: v1.9.4 (data transformation)
- **JupyterLab**: v4.3.4 (AI analytics)

## 🔧 Common Operations

### Starting/Stopping Services
```bash
# Start all services
docker-compose up -d

# Stop all services  
docker-compose down

# Restart a specific service
docker-compose restart superset

# View logs
docker-compose logs -f dagster
```

### Database Operations
```bash
# Initialize fresh databases
python init_duckdb.py

# Run dbt transformations
docker-compose exec dbt dbt run

# Test dbt models
docker-compose exec dbt dbt test
```

### Development Workflow
1. Add raw data files to `01_source_data/`
2. Create Dagster assets in `03_dagster/definitions.py` 
3. Build dbt models in `04_dbt/models/`
4. Define Cube schema in `05_cube_dev/schema/`
5. Create Superset dashboards via UI
6. Analyze with PandasAI in Jupyter notebooks

## 🔌 Connecting Services to Data

### Superset Database Connections

**Important**: Superset configurations now persist across container restarts in the `06_superset/data/` directory.

1. **Access Superset**: http://localhost:8088 (admin/admin)
2. **Add DuckDB Databases**:
   - Navigate to **Settings** → **Database Connections** → **+ DATABASE**
   - Choose **Other** for database type

3. **Connection URIs** (copy exactly):

   **Raw Database (Read-Only)**:
   ```
   duckdb:////app/02_duck_db/01_raw/raw.duckdb
   ```

   **Dev Database (Development)**:
   ```
   duckdb:////app/02_duck_db/02_dev/dev.duckdb
   ```

   **Prod Database (Production)**:
   ```
   duckdb:////app/02_duck_db/03_prod/prod.duckdb
   ```

4. **Configure Read-Only Access** (for Raw and Prod):
   - After entering the URI, click the **"Advanced"** tab
   - In the **"Engine Parameters"** section, add:
     ```json
     {
         "connect_args": {
             "read_only": true
         }
     }
     ```

5. **Test Connection**: Click "Test Connection" before saving
6. **Naming Convention**: Use descriptive names like "DuckDB Raw", "DuckDB Dev", "DuckDB Prod"

### Jupyter Database Test Query

**Test DuckDB Connection in Jupyter**:

1. **Access Jupyter**: http://localhost:8888 (use token from logs)
2. **Create New Notebook**: Python 3
3. **Run Test Query**:

```python
import duckdb
import pandas as pd
import os

# Connect to Raw DuckDB (read-only)
raw_db_path = "/app/02_duck_db/01_raw/raw.duckdb"
dev_db_path = "/app/02_duck_db/02_dev/dev.duckdb"

# Test raw database connection
try:
    conn_raw = duckdb.connect(raw_db_path, read_only=True)
    print("✅ Connected to Raw DuckDB successfully!")
    
    # Show available schemas
    schemas = conn_raw.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
    print(f"📁 Available schemas: {schemas}")
    
    # Show tables in each schema (if any)
    for schema in schemas:
        schema_name = schema[0]
        if schema_name not in ['information_schema', 'pg_catalog']:  # Skip system schemas
            tables = conn_raw.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}'").fetchall()
            print(f"📊 Tables in {schema_name}: {[t[0] for t in tables]}")
    
    conn_raw.close()
    
except Exception as e:
    print(f"❌ Error connecting to Raw DuckDB: {e}")

# Test dev database connection  
try:
    conn_dev = duckdb.connect(dev_db_path)
    print("✅ Connected to Dev DuckDB successfully!")
    
    # Create a simple test
    conn_dev.execute("CREATE SCHEMA IF NOT EXISTS test")
    conn_dev.execute("CREATE TABLE IF NOT EXISTS test.sample AS SELECT 1 as id, 'test' as name")
    
    # Query the test table
    result = conn_dev.execute("SELECT COUNT(*) as record_count FROM test.sample").fetchone()
    print(f"📈 Test query result: {result[0]} records in test.sample table")
    
    conn_dev.close()
    
except Exception as e:
    print(f"❌ Error with Dev DuckDB: {e}")

print("\n🎯 Platform Status: DuckDB connections are operational!")
```

4. **Expected Output**:
   ```
   ✅ Connected to Raw DuckDB successfully!
   📁 Available schemas: [('main',), ('information_schema',)]
   📊 Tables in main: []
   📊 Tables in information_schema: [...]
   ✅ Connected to Dev DuckDB successfully!
   📈 Test query result: 1 records in test.sample table
   🎯 Platform Status: DuckDB connections are operational!
   ```

### **⚠️ Important: Jupyter Database Connection Best Practices**

To prevent DuckDB lock conflicts when using Jupyter notebooks:

1. **Always close connections**: Use `conn.close()` in every notebook cell that opens a database connection
2. **Use context managers** when possible:
   ```python
   import duckdb
   
   # Recommended approach
   with duckdb.connect("/app/02_duck_db/01_raw/raw.duckdb", read_only=True) as conn:
       result = conn.execute("SELECT COUNT(*) FROM raw.taxi_trips").fetchone()
       print(f"Record count: {result[0]}")
   # Connection automatically closed
   ```
3. **Restart kernel** if you encounter lock errors: `Kernel` → `Restart Kernel`
4. **Use read-only connections** for analysis when possible to avoid conflicts with Dagster operations

## ✅ End-to-End Platform Validation

This comprehensive validation workflow ensures all platform components work together seamlessly. Complete these steps in order to verify your platform is ready for Phase 2 development.

### **Prerequisites**
- All services running: `docker-compose ps` shows all services "Up"
- Sample data available (the platform includes NYC taxi data examples)

### **Step 1: Data Ingestion with Dagster**
1. **Access Dagster UI**: http://localhost:3000
2. **Materialize Raw Assets**:
   - Navigate to "Assets" in the left sidebar
   - Look for assets in the "raw_data_ingestion" group: `taxi_trips_raw` and `taxi_zones_raw`
   - Click "Materialize all" or select individual assets and click "Materialize selected"
3. **Verify Success**:
   - Check that asset runs completed successfully (green checkmarks)
   - Review logs for row counts (should show data loaded)
   - **Expected Result**: Raw data loaded into `raw.duckdb` in the `raw` schema

### **Step 2: Data Transformation with dbt**
1. **Run dbt Transformations**:
   ```bash
   docker-compose exec dbt dbt run --target prod
   ```
2. **Verify Output**:
   - Look for "PASS=2" indicating successful model builds
   - Models created: `stg_taxi_trips` (view) and `mart_taxi_trips` (table)
3. **Test dbt Models** (optional):
   ```bash
   docker-compose exec dbt dbt test --target prod
   ```
   - **Expected Result**: Transformed data available in `prod.duckdb` in `stg` and `mart` schemas

### **Step 3: Business Intelligence with Superset**
1. **Access Superset**: http://localhost:8088 (admin/admin)
2. **Connect to Production Database**:
   - Navigate to **Settings** → **Database Connections** → **+ DATABASE**
   - Database name: "DuckDB Prod"
   - URI: `duckdb:////app/02_duck_db/03_prod/prod.duckdb`
   - Click **Advanced** → **Engine Parameters**:
     ```json
     {
         "connect_args": {
             "read_only": true
         }
     }
     ```
   - **Test Connection** and **Save**
3. **Create a Simple Chart**:
   - Navigate to **SQL** → **SQL Lab**
   - Select "DuckDB Prod" database
   - Run query: `SELECT COUNT(*) as trip_count FROM mart.mart_taxi_trips`
   - Click **Explore** to create a visualization
   - Save the chart with a descriptive name
4. **Expected Result**: Chart displays trip count from transformed data

### **Step 4: Semantic Layer with Cube.js**
1. **Access Cube Dev Server**: http://localhost:4000
2. **Verify Schema Connection**:
   - The "Empty DB Schema" error should be resolved
   - You should see database connection status as active
   - Schema browser should show available tables from `prod.duckdb`
3. **Browse Available Data**:
   - Navigate through the schema browser
   - Confirm `mart_taxi_trips` table is visible and accessible
4. **Expected Result**: Cube.js can successfully read from populated production database

### **Step 5: AI-Powered Analysis with Jupyter**
1. **Access Jupyter**: http://localhost:8888 (use token from logs)
2. **Create New Notebook**: Python 3
3. **Run AI Analysis Query**:
   ```python
   import duckdb
   import pandas as pd
   
   # Connect to production database (read-only for safety)
   with duckdb.connect("/app/02_duck_db/03_prod/prod.duckdb", read_only=True) as conn:
       # Query the final mart table
       df = conn.execute("""
           SELECT 
               pickup_borough,
               COUNT(*) as trip_count,
               AVG(trip_distance) as avg_distance,
               AVG(total_amount) as avg_fare
           FROM mart.mart_taxi_trips 
           GROUP BY pickup_borough 
           ORDER BY trip_count DESC
           LIMIT 5
       """).df()
       
   print("🚖 Top 5 Boroughs by Trip Count:")
   print(df)
   
   # Optional: Test PandasAI integration (requires API key)
   try:
       from pandasai import Agent
       agent = Agent(df)
       response = agent.chat("What borough has the highest average fare?")
       print(f"\n🤖 PandasAI Response: {response}")
   except Exception as e:
       print(f"\n📝 PandasAI not configured (API key needed): {e}")
   ```
4. **Expected Result**: Query executes successfully, showing transformed data is accessible for AI analysis

### **🎯 Validation Checklist**

Mark each item as complete:

- [ ] **Dagster**: Raw data assets materialized successfully
- [ ] **dbt**: Models built in production database without errors  
- [ ] **Superset**: Connected to prod database and created visualization
- [ ] **Cube.js**: Schema browser shows production data, no "Empty DB" error
- [ ] **Jupyter**: Successfully queried mart tables and data flows correctly

### **✅ Success Criteria**

If all steps complete successfully, you have:
1. **End-to-end data flow**: Raw → Staging → Mart
2. **Service integration**: All tools can access and work with the same data
3. **Persistence verification**: Data survives service restarts
4. **Ready for Phase 2**: Platform is stable and ready for custom data workflows

**🚀 Congratulations!** Your analytics-to-AI platform is fully operational and ready for production use.

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs [service-name]

# Common fixes
docker-compose down && docker-compose up -d
docker system prune  # Clean up Docker resources
```

### Port Already in Use
```bash
# Find process using port
netstat -tulpn | grep :3000

# Kill process or change port in docker-compose.yml
```

### Database Connection Issues
- **DuckDB locked**: Only one writer allowed. Stop other connections or use read-only mode
- **File permissions**: Ensure Docker can write to `02_duck_db/` directories
- **Database not initialized**: Run `python init_duckdb.py`

### Superset Login Issues
- Default: admin/admin
- Reset: `docker-compose exec superset superset fab create-admin`

### Jupyter Token Missing
```bash
# Get token from logs
docker-compose logs jupyter | grep token=
```

### Memory Issues
- Minimum 4GB RAM recommended
- Adjust Docker Desktop memory limits
- Stop unused services: `docker-compose stop [service]`

## 🔄 Updating Dependencies

### Safe Update Process
1. **Check release notes** for breaking changes
2. **Update version** in requirements.txt files
3. **Backup databases** (copy `02_duck_db/` folder)  
4. **Rebuild containers**:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```
5. **Test services** using validation steps above
6. **Run in dev environment** before prod

## 💾 Data Persistence Strategy

All user work and configurations are automatically preserved across container restarts. Here's what persists for each service:

### **Persistent Data Locations**

| Service | What Persists | Host Location | Container Mount |
|---------|---------------|---------------|-----------------|
| **Superset** | Database connections, dashboards, charts, users | `./06_superset/data/` | `/home/superset/.superset` |
| **Dagster** | Run history, schedules, asset metadata | `./03_dagster/dagster_home/` | `/opt/dagster/dagster_home` |
| **Jupyter** | Notebooks (.ipynb), custom scripts | `./07_pandas_ai/` | `/app/07_pandas_ai` |
| **DuckDB** | All database files (raw, dev, prod) | `./02_duck_db/` | `/app/02_duck_db` |
| **dbt** | Models, configurations (code-based) | `./04_dbt/` | `/app/04_dbt` |
| **Cube** | Schema definitions (code-based) | `./05_cube_dev/` | `/app/05_cube_dev` |

### **What Gets Saved**

- ✅ **Superset**: All dashboards, charts, database connections, user accounts, and custom configurations
- ✅ **Dagster**: Complete run history, pipeline schedules, asset lineage, and operational metadata
- ✅ **Jupyter**: All notebooks you create or modify, including PandasAI experiments
- ✅ **DuckDB**: All data tables, schemas, and database state across raw/dev/prod environments
- ✅ **dbt**: All SQL models, configurations, and transformations (version controlled)
- ✅ **Cube**: All semantic layer definitions and API configurations (version controlled)

### **Backup Recommendations**

For critical work, consider backing up these directories:
```bash
# Essential data directories
cp -r 02_duck_db/ backup/duck_db_$(date +%Y%m%d)/
cp -r 06_superset/data/ backup/superset_$(date +%Y%m%d)/
cp -r 07_pandas_ai/ backup/notebooks_$(date +%Y%m%d)/
```

## 📊 DuckDB Concurrency Notes

- **Single writer, multiple readers** architecture
- **Read-only services**: Superset, Cube (safe for concurrent access)
- **Write services**: Dagster, dbt (coordinate writes through orchestration)
- **If locks occur**: Consider PostgreSQL for high-concurrency scenarios

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

---

**Ready to start? Run `docker-compose up -d` and visit the service URLs above!**
