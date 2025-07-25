| Tool / Software | Official Package Name  | Golden Version | Critical Notes |
| :-------------- | :--------------------- | :------------- | :------------- |
| Python          | python                 | 3.11.8         |                |
| DuckDB          | duckdb                 | 1.3.2          |                |
| **DuckDB Engine**| **duckdb-engine**      | **0.6.5**      | **⚠️ CRITICAL: v0.13.0 breaks Superset 5.0.0** |
| Dagster         | dagster                | 1.11.2         |                |
| dbt-core        | dbt-core               | 1.9.4          |                |
| **Apache Superset**| **apache-superset**  | **5.0.0**      | **✅ UPGRADED: Now stable with duckdb-engine 0.6.5** |
| Cube.js Server  | @cubejs-backend/server | 1.3.41         |                |
| PandasAI        | pandasai               | 2.3.0          |                |
| JupyterLab      | jupyterlab             | 4.3.4          |                |
| NumPy           | numpy                  | 1.24.4         |                |
| Pandas          | pandas                 | 1.5.3          |                |
| Polars          | polars                 | 1.15.0         |                |

## Known Compatibility Issues

### Superset 5.0.0 + DuckDB Engine
- **WORKING**: `apache-superset==5.0.0` + `duckdb-engine==0.6.5` + `duckdb==1.3.2`
- **BROKEN**: `apache-superset==5.0.0` + `duckdb-engine==0.13.0` (causes "'dict' object has no attribute 'set'" error)
- **Fix Applied**: 2025-07-25 - Pinned duckdb-engine to 0.6.5 in Superset requirements.txt
