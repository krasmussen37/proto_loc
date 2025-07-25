# Claude AI Memory - Phase 2: Analytics Development

## Phase 2 Mission
Transform the empty platform into a **value-generating analytics system** by loading proprietary data and building insights for business impact.

## Analytics Development Workflow

### 🟢 Data Integration (Dagster)
**Impact Level**: Medium - affects all downstream analytics
```python
# Pattern for new data sources
@asset
def raw_sales_data():
    """Load sales data to raw schema"""
    # ALWAYS use raw schema for source data
    # ALWAYS handle DuckDB write locks
    # ALWAYS document source system
```

### 🟡 Data Transformation (dbt)
**Impact Level**: High - breaks dashboards if done wrong
```sql
-- Pattern for staging models
{{ config(
    materialized='table',
    schema='stg'
) }}

SELECT 
    -- ALWAYS cast data types explicitly
    -- ALWAYS handle nulls
    -- ALWAYS add data quality tests
```

### 🔵 Semantic Layer (Cube.js)
**Impact Level**: Medium - affects business users
```javascript
// Pattern for business metrics
cube('Revenue', {
  sql: 'SELECT * FROM mart.fct_revenue',
  
  measures: {
    totalRevenue: {
      sql: 'revenue_amount',
      type: 'sum',
      description: 'Total revenue in USD' // ALWAYS document
    }
  }
});
```

### 🟣 Visualization (Superset)
**Impact Level**: Low - UI only but must persist
- Create datasets from mart tables only
- Build charts iteratively
- Save dashboards frequently
- Export as JSON for version control

## Data Flow Best Practices

### Source → Raw
```python
# GOOD: Incremental loading with state tracking
@asset
def raw_orders(context):
    last_loaded = context.resources.state.get_last_loaded_timestamp()
    new_data = fetch_orders_since(last_loaded)
    
    # Handle DuckDB single-writer constraint
    with duckdb.connect(RAW_DB_PATH, read_only=False) as conn:
        conn.execute("INSERT INTO orders SELECT * FROM new_data")
```

### Raw → Staging
```sql
-- GOOD: Clean and standardize
WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),
cleaned AS (
    SELECT
        order_id::VARCHAR AS order_id,
        COALESCE(customer_id, 'UNKNOWN') AS customer_id,
        order_date::DATE AS order_date,
        -- Standardize amount to 2 decimal places
        ROUND(order_amount::DECIMAL(10,2), 2) AS order_amount
    FROM source
    WHERE order_date IS NOT NULL  -- Remove invalid records
)
SELECT * FROM cleaned
```

### Staging → Marts
```sql
-- GOOD: Business logic in marts
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
final AS (
    SELECT
        o.order_date,
        c.customer_segment,
        c.customer_region,
        SUM(o.order_amount) AS daily_revenue,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        COUNT(o.order_id) AS order_count
    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id
    GROUP BY 1, 2, 3
)
SELECT * FROM final
```

## Common Analytics Patterns

### Time Series Analysis
```sql
-- Pattern: Rolling metrics
WITH daily_metrics AS (
    SELECT 
        date,
        SUM(revenue) AS daily_revenue
    FROM mart.fct_revenue
    GROUP BY date
)
SELECT
    date,
    daily_revenue,
    AVG(daily_revenue) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS revenue_7day_avg,
    AVG(daily_revenue) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS revenue_30day_avg
FROM daily_metrics
```

### Cohort Analysis
```sql
-- Pattern: Customer cohorts
WITH first_purchase AS (
    SELECT 
        customer_id,
        MIN(order_date) AS cohort_date
    FROM mart.fct_orders
    GROUP BY customer_id
),
cohort_revenue AS (
    SELECT
        fp.cohort_date,
        DATE_DIFF('month', fp.cohort_date, o.order_date) AS months_since_first,
        COUNT(DISTINCT o.customer_id) AS active_customers,
        SUM(o.revenue) AS cohort_revenue
    FROM mart.fct_orders o
    JOIN first_purchase fp ON o.customer_id = fp.customer_id
    GROUP BY 1, 2
)
SELECT * FROM cohort_revenue
```

### Data Quality Monitoring
```yaml
# Pattern: dbt tests for data quality
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: order_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
      - name: order_date
        tests:
          - not_null
          - dbt_utils.date_is_in_the_past
```

## Iteration Guidelines

### Safe Iteration Pattern
1. **Development Branch**: Create feature branch
2. **Test Locally**: Run transformations on dev.duckdb
3. **Preview Impact**: Check affected downstream models
4. **Update Tests**: Add data quality checks
5. **Document Changes**: Update model descriptions
6. **Gradual Rollout**: Deploy to dev → staging → prod

### Breaking Change Protocol
When changing existing marts:
1. Create new version (e.g., `fct_revenue_v2`)
2. Run both versions in parallel
3. Migrate dashboards incrementally
4. Deprecate old version after validation
5. Clean up after full migration

## Frontend Development Patterns

### Superset Best Practices
```python
# Dataset configuration
{
    "database": "DuckDB Dev",  # Always use dev for testing
    "schema": "mart",          # Only expose mart layer
    "table": "fct_revenue",
    "cache_timeout": 300,      # 5 minute cache
    "filter_select_enabled": True
}
```

### Dashboard Persistence
1. **Auto-save**: Enable in Superset settings
2. **Manual Export**: Dashboard → Actions → Export to JSON
3. **Version Control**: Store exports in `06_superset/dashboards/`
4. **Import Process**: Document in README

### Chart Development Workflow
1. Start with simple table view
2. Validate numbers match source
3. Apply appropriate visualization
4. Add filters and drill-downs
5. Test with different date ranges
6. Document business logic

## Performance Optimization

### Query Optimization
```sql
-- GOOD: Push filters down
WITH filtered_orders AS (
    SELECT * FROM orders 
    WHERE order_date >= '2024-01-01'  -- Filter early
)

-- BAD: Filter after join
WITH all_data AS (
    SELECT * FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
)
SELECT * FROM all_data WHERE order_date >= '2024-01-01'
```

### Materialization Strategy
- **Views**: For simple transformations
- **Tables**: For complex joins or aggregations
- **Incremental**: For large fact tables (Phase 2 only)

## Common Pitfalls

### ❌ Exposing Raw Data
Never create Superset datasets from raw schema

### ❌ Complex Logic in BI Layer
Keep calculations in dbt, not Superset

### ❌ Ignoring Data Quality
Always add tests before promoting to production

### ❌ Breaking Existing Dashboards
Test impact before modifying mart tables

## Debugging Patterns

### Data Discrepancies
1. Check source data quality
2. Validate transformation logic
3. Review join conditions
4. Check for duplicates
5. Verify date/time handling

### Performance Issues
1. Analyze query execution plan
2. Check for missing indexes
3. Review materialization strategy
4. Consider pre-aggregation
5. Monitor DuckDB file size

## Next Steps for Analytics Development
1. Establish data refresh schedule
2. Create standard KPI definitions
3. Build reusable dbt macros
4. Set up data quality monitoring
5. Document business logic