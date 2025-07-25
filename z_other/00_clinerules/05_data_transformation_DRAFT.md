# Data transformation development considerations
## Future considerations
- [ ] DuckDB Single-Writer Pattern: When creating dbt transformations or custom Dagster transformation assets that write to DuckDB databases, ensure coordination with raw data ingestion to prevent concurrent writes to the same database file. Consider using explicit Dagster asset dependencies to enforce sequential execution order between ingestion and transformation phases.
- [ ]  [ OPEN ]

----
