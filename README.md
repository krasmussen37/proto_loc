# proto_loc | Analytics-to-AI Platform

A full-stack, local-first analytics and AI platform that mirrors enterprise cloud capabilities. Built for rapid prototyping, training, and community demonstration.

## Phase 1: Infrastructure Complete ✅

The platform infrastructure is now fully operational with all services connected and communicating successfully. Key achievements:

- **✅ All Docker services running stably** with persistent data storage
- **✅ DuckDB successfully integrated** as the analytical database across all three environments (raw, dev, prod)
- **✅ Superset connected to all DuckDB instances** with proper read-only configurations to prevent locking
- **✅ End-to-end data flow established** from raw ingestion through transformation to visualization
- **✅ Sample NYC taxi data loaded** and available for analysis and dashboard creation

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/krasmussen37/proto_loc.git
cd proto_loc

# Configure environment variables (copy and edit .env file)
cp .env.example .env
# Edit .env to add your API keys for AI services (OpenAI, Anthropic, etc.)

# Initialize DuckDB databases
python init_duckdb.py

# Launch all platform services
docker-compose up -d
```

### 2. Platform Services & Access

| Service | URL | Default Login | Purpose |
|---------|-----|---------------|---------|
| **Superset** | http://localhost:8088 | admin / admin | BI & Dashboards |
| **Dagster** | http://localhost:3000 | No login required | Data Orchestration |
| **Jupyter** | http://localhost:8888 | Token-based (see logs) | AI-Powered Analysis |
| **PostgreSQL** | Internal (port 5432) | superset / superset | Application Metadata Store |
| **Cube** | http://localhost:4000 | Currently disabled | Semantic Layer |

#### Getting Jupyter Access Token
```bash
# Get the Jupyter access token
docker-compose logs jupyter | grep "token="
# Use the token shown in the URL to access Jupyter
```

### 3. Essential: Connect DuckDB Databases to Superset

**Important:** After launching the services, you must manually connect the DuckDB databases in Superset:

1. **Access Superset**: Go to http://localhost:8088 and login with `admin` / `admin`

2. **Add Database Connections**: Go to Settings → Database Connections → + DATABASE

3. **Select DuckDB** from the database list

4. **Configure each database** with these **exact** settings:

   **Raw Database (Read-Only):**
   - Database Name: `proto_loc_raw`
   - SQLAlchemy URI: `duckdb:////app/02_duck_db/01_raw/raw.duckdb`
   - Advanced Tab → Engine Parameters:
     ```json
     {
         "connect_args": {
             "read_only": true
         }
     }
     ```

   **Dev Database (Read-Only for BI):**
   - Database Name: `proto_loc_dev`
   - SQLAlchemy URI: `duckdb:////app/02_duck_db/02_dev/dev.duckdb`
   - Advanced Tab → Engine Parameters:
     ```json
     {
         "connect_args": {
             "read_only": true
         }
     }
     ```

   **Prod Database (Read-Only for BI):**
   - Database Name: `proto_loc_prod`
   - SQLAlchemy URI: `duckdb:////app/02_duck_db/03_prod/prod.duckdb`
   - Advanced Tab → Engine Parameters:
     ```json
     {
         "connect_args": {
             "read_only": true
         }
     }
     ```

5. **Test Each Connection**: Click "TEST CONNECTION" before saving each database.

**Why Read-Only?** The `read_only: true` setting prevents Superset from acquiring write locks on DuckDB files, allowing multiple services (Dagster, dbt, Superset) to access the same databases simultaneously without conflicts.

## Phase 2: End-to-End Pipeline Validation

With infrastructure complete, the next phase focuses on validating the complete analytics-to-AI workflow:

- **✅ Raw Data Available**: NYC taxi dataset pre-loaded in DuckDB raw database
- **⏳ Next: dbt Modeling**: Transform raw data into business-ready marts
- **⏳ Dashboard Creation**: Build interactive visualizations in Superset  
- **⏳ AI Analysis**: Leverage PandasAI for natural language data queries
- **⏳ Semantic Layer**: Configure Cube for consistent metrics (when re-enabled)

## Data Flow Architecture

```
Raw Data (CSV) → DuckDB Raw → dbt Transform → DuckDB Dev/Prod → Superset Dashboards
                                     ↓
                         Jupyter + PandasAI (AI Analysis)
```

## Project Structure

```
proto_loc/
├── 00_clinerules/          # Project rules and guidelines
├── 01_source_data/         # Raw source data files (CSV, etc.)
├── 02_duck_db/           # DuckDB databases
│   ├── 01_raw/          # Raw ingestion layer (source truth)
│   ├── 02_dev/          # Development environment (for testing)
│   └── 03_prod/         # Production environment (for dashboards)
├── 03_dagster/          # Data orchestration & pipeline management
├── 04_dbt/              # Data transformation & modeling
├── 05_cube_dev/         # Semantic layer (temporarily disabled)
├── 06_superset/         # BI platform & dashboard creation
├── 07_pandas_ai/        # AI-powered analytics & natural language queries
├── other/               # Supporting code, utilities, and workplan
└── README.md
```

## Advanced Configuration

### Environment Variables (.env)

The platform uses environment variables for AI service integration:

```bash
# AI Services (Optional - for PandasAI features)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GROQ_API_KEY=your-groq-key-here
GOOGLE_API_KEY=your-gemini-key-here

# Service Ports (Optional - defaults provided)
DAGSTER_PORT=3000
SUPERSET_PORT=8088
JUPYTER_PORT=8888
CUBE_PORT=4000
```

### Troubleshooting

**DuckDB Connection Issues:**
- Ensure all services are running: `docker-compose ps`
- Check Superset logs: `docker-compose logs superset`
- Verify database files exist: `ls -la 02_duck_db/*/`

**Service Access Issues:**
- Wait for services to fully initialize (especially Superset ~90 seconds)
- Check service health: `docker-compose logs [service-name]`
- Restart if needed: `docker-compose restart [service-name]`

## Contributing

This is an open-source project. Contributions are welcome! Please see the `/00_clinerules/` directory for development guidelines and project standards.

## License

MIT License - see LICENSE file for details

---

**🎯 Ready to Get Started?** 
1. Follow the Quick Start above
2. Connect the DuckDB databases in Superset (essential!)
3. Start exploring the pre-loaded taxi data
4. Build your first dashboard or run AI queries in Jupyter

For detailed development guidelines, see the documentation in `/00_clinerules/`.
