# Data Modeling & Semantic Layer Guidelines (proto_loc Analytics Platform)

## Future considerations
- [ ] Advanced dbt macro patterns for common transformation logic
- [ ] Incremental model strategies for large datasets
- [ ] Data lineage documentation standards
- [ ] Cross-database query optimization patterns
- [ ] Automated data quality monitoring workflows
- [ ] Advanced semantic layer patterns (calculated measures, time intelligence)
- [ ] Multi-tenant data modeling approaches
- [ ] Real-time streaming data integration patterns

----
## Overview

This document establishes the comprehensive naming conventions, data modeling standards, and semantic layer architecture for the proto_loc analytics platform. These guidelines ensure consistency across all databases, schemas, tables, and analytical objects throughout the analytics-to-AI pipeline.

## Database & Schema Naming Standards

### **Database Structure**

The platform uses **three distinct DuckDB databases** to maintain clear separation of concerns:

```
02_duck_db/
├── 01_raw/raw.duckdb        # Raw ingestion layer
├── 02_dev/dev.duckdb        # Development environment  
└── 03_prod/prod.duckdb      # Production environment
```

### **Schema Organization by Database**

#### **Raw Database (`raw.duckdb`)**
- **Purpose**: Store unmodified source data exactly as ingested
- **Schema Pattern**: `<source_system>` 
- **Examples**:
  - `nyc_taxi` - NYC Yellow Taxi data source
  - `crm` - Customer Relationship Management system
  - `erp` - Enterprise Resource Planning system
  - `sales_force` - Salesforce CRM exports
  - `google_analytics` - Web analytics data

#### **Development & Production Databases (`dev.duckdb`, `prod.duckdb`)**
- **Purpose**: Transformed, business-ready data for analytics consumption
- **Schema Pattern**: Fixed two-schema structure
  - `stg` - Staging models (cleaned, standardized data)
  - `mart` - Data marts (final business models)

### **Table Naming Conventions**

#### **Raw Layer Tables**
- **Pattern**: `<source_system>.<descriptive_table_name>`
- **Format**: `snake_case` (all lowercase with underscores)
- **Examples**:
  - `nyc_taxi.yellow_trips`
  - `nyc_taxi.taxi_zones_lookup`
  - `crm.customers_raw`
  - `crm.transactions_raw`
  - `erp.inventory_snapshot`

#### **Staging Layer Tables/Views**
- **Pattern**: `stg.<object_name>`
- **Format**: `<source>_<object or transformation purpose>` 
- **Examples**:
  - `stg.nyc_taxi_trips_data_type_mods`
  - `stg.nyc_taxi_zones_date_parse`
  - `stg.crm_customers_regex`
  - `stg.crm_transactions`

#### **Mart Layer Tables**
- **Pattern**: `mart.<business_object_name>`
- **Format**: `<type>_<business_entity>`
- **Types**:
  - `fct_` - Fact tables (transactional/event data)
  - `dim_` - Dimension tables (reference/lookup data)
  - `mart_` - Denormalized analytical tables
- **Examples**:
  - `mart.fct_taxi_trips`
  - `mart.dim_taxi_zones`
  - `mart.mart_customer_summary`
  - `mart.fct_sales_transactions`

## Data Modeling Standards

### **Materialization Strategy**

#### **Raw Layer**
- **Materialization**: Physical **tables** only
- **Rationale**: Preserve exact source data for audit and lineage
- **Refresh**: Full reload on each ingestion cycle, incremental if practicable

#### **Staging Layer**
- **Default Materialization**: **Views** 
- **Rationale**: Lightweight transformations, always current with raw data
- **Exception**: Materialize as **table** if transformation is computationally expensive
- **dbt Configuration**: `materialized: view` (default)

#### **Mart Layer**  
- **Default Materialization**: **Tables**
- **Rationale**: Optimized for query performance and end-user consumption
- **Refresh Strategy**: 
  - **Full refresh** for smaller datasets (< 1M rows)
  - **Incremental** for large datasets with clear timestamp columns
- **dbt Configuration**: `materialized: table` or `materialized: incremental`

### **Column Naming Standards**

- **Format**: `snake_case` (consistent across all layers)
- **Primary Keys**: `<table_name>_id` (e.g., `customer_id`, `trip_id`)
- **Foreign Keys**: Match referenced table's primary key name
- **Timestamps**: Use descriptive names
  - `created_at`, `updated_at`, `deleted_at`
  - `trip_start_time`, `trip_end_time`
- **Boolean Fields**: Use `is_` or `has_` prefixes
  - `is_active`, `has_discount`, `is_deleted`
- **Monetary Fields**: Include currency context
  - `amount_usd`, `total_cost_usd`, `fare_amount_usd`

### **Data Type Standardization**

#### **Common Data Types**
- **Identifiers**: `VARCHAR` (flexible length)
- **Timestamps**: `TIMESTAMP` (with timezone awareness where applicable)
- **Monetary**: `DECIMAL(10,2)` for currency amounts
- **Percentages**: `DECIMAL(5,4)` (supports 0.0001 precision)
- **Boolean**: `BOOLEAN` 
- **Geographic**: Use DuckDB spatial extensions for coordinates

#### **Null Handling**
- **Staging Layer**: Preserve nulls from source, document meaning
- **Mart Layer**: Apply business rules for null handling
- **Documentation**: Always document null semantics in dbt model descriptions

## Semantic Layer Architecture (Cube.js)

### **Cube Naming Standards**

#### **Cube Definition Names**
- **Pattern**: `<BusinessDomain><EntityType>`
- **Format**: PascalCase (to align with JavaScript conventions)
- **Examples**:
  - `TaxiTrips` (from `mart.fct_taxi_trips`)
  - `TaxiZones` (from `mart.dim_taxi_zones`)
  - `CustomerSummary` (from `mart.mart_customer_summary`)

#### **Measure Naming**
- **Pattern**: `<aggregation><field><unit>`
- **Format**: camelCase
- **Examples**:
  - `totalFareAmount`
  - `avgTripDistance`
  - `countTrips`
  - `sumTipAmount`

#### **Dimension Naming**
- **Pattern**: `<descriptive_name>`
- **Format**: camelCase
- **Examples**:
  - `pickupZone`
  - `dropoffZone`
  - `tripDate`
  - `paymentType`

### **Cube File Organization**

```
05_cube_dev/schema/
├── facts/
│   ├── TaxiTrips.js
│   └── SalesTransactions.js
├── dimensions/
│   ├── TaxiZones.js
│   └── CustomerDimension.js
└── shared/
    └── CommonMeasures.js
```

## Development Environment Rules

### **Database Connection Patterns**

#### **Development Workflow**
1. **Raw Ingestion**: Always write to `raw.duckdb`
2. **Model Development**: Always develop against `dev.duckdb`
3. **Production Promotion**: Manual human-approved deployment to `prod.duckdb`

#### **dbt Target Configuration**
```yaml
# profiles.yml
proto_loc_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../02_duck_db/02_dev/dev.duckdb
      schema: main
    prod:
      type: duckdb  
      path: ../02_duck_db/03_prod/prod.duckdb
      schema: main
```

### **Cross-Environment Consistency**

- **Schema Structure**: Identical across dev and prod databases
- **Table Names**: Identical across environments
- **Data Types**: Consistent type definitions
- **Business Logic**: Same transformations, different data volumes

## Quality & Testing Standards

### **dbt Testing Strategy**

#### **Staging Layer Tests**
- **Unique**: Primary key columns
- **Not Null**: Critical business fields
- **Relationships**: Foreign key integrity with raw layer
- **Accepted Values**: Categorical fields with known domains

#### **Mart Layer Tests**
- **Unique**: Primary keys and natural business keys
- **Not Null**: All dimension keys and critical measures
- **Relationships**: Cross-table referential integrity
- **Custom Tests**: Business rule validation

### **Dev vs prod testing**
+ Mart table record count checks between dev and prod
+ Mart table key field sums and variances checked between dev and prod
+ While development is ongoing variances are expected, but post push to prod there should be no variances

### **Data Freshness Monitoring**

- **Raw Layer**: Monitor file ingestion timestamps
- **Staging/Mart**: Use dbt freshness tests on time-based partitions
- **Alerting**: Configure Dagster sensors for data quality failures

## Integration Points

### **Superset Integration**

- **Database Connections**: 
  - `proto_loc_raw` → `raw.duckdb` (raw data explore for troubleshooting)
  - `proto_loc_dev` → `dev.duckdb` (development dashboards)
  - `proto_loc_prod` → `prod.duckdb` (production dashboards)
- **Table Access**: Query mart tables directly for dashboard creation
- **Naming**: Dashboard titles should match mart table business names

### **PandasAI Integration**

- **Data Access**: Connect to appropriate database based on use case
  - Development/exploration: `dev.duckdb`
  - Production analysis: `prod.duckdb` (read-only)
- **Table References**: Use full schema.table syntax in queries
- **Column References**: Use documented business-friendly column names
