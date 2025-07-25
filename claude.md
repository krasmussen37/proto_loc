# Claude AI Assistant Memory - proto_loc Analytics Platform

## Project Phase Awareness

### Phase 1: Infrastructure Platform (Current Focus)
- **Goal**: Create a stable, empty analytics platform that can be forked
- **Users**: Developers who want to spin up a robust analytics stack quickly
- **Key Deliverable**: Clean, working infrastructure with no proprietary data

### Phase 2: Analytics Implementation
- **Goal**: Use the platform for actual business analysis with real data
- **Users**: Data teams loading proprietary data for business impact
- **Key Deliverable**: Insights and analytics from loaded data

## Development Type Decision Framework

Before ANY modification, ask yourself:

### 1. Infrastructure Development 🔴 HIGH IMPACT
**What**: Docker configs, Superset settings, core tool configurations
**When**: Rarely - only when improving the base platform
**Impact**: Affects ALL forks and downstream projects
**Before changing**: 
- Consider impact on existing forks
- Document in golden_versions.md
- Test extensively
- Update README.md

### 2. Analytics/Data Development 🟡 MEDIUM IMPACT  
**What**: dbt models, Dagster assets, Python scripts, SQL
**When**: Frequently in Phase 2
**Impact**: Affects data consumers and dashboards
**Before changing**:
- Check impact on downstream marts
- Consider refresh schedules
- Update documentation

### 3. Frontend/No-Code Development 🟢 LOW IMPACT
**What**: Superset charts, dashboards, Cube.js playground
**When**: Continuously in Phase 2
**Impact**: UI/UX only, but must persist correctly
**Before changing**:
- Ensure persistence mechanism exists
- Test configuration survives restart
- Export configurations if needed

## Critical Technical Constraints

### DuckDB Single-Writer Lock
- **Rule**: Only ONE process can write to DuckDB at a time
- **Solution**: Sequential execution in Dagster for all writes
- **Impact**: All BI tools MUST use read-only connections

### Golden Versions Policy
- **Location**: `.clinerules/golden_versions.md`
- **Rule**: NEVER downgrade versions to fix issues
- **Reason**: Maintains compatibility across all forks

## Project Structure & Standards

### Repository Organization
```
proto_loc/
├── 00_clinerules/        # Draft rules (AI can modify)
├── .clinerules/          # Official rules (human-edited only)
├── 01_source_data/       # Raw data files
├── 02_duck_db/           # DuckDB databases
│   ├── 01_raw/          # Source data
│   ├── 02_dev/          # Development 
│   └── 03_prod/         # Production (human approval required)
├── 03_dagster/          # Orchestration
├── 04_dbt/              # Transformations
├── 05_cube_dev/         # Semantic layer
├── 06_superset/         # Visualization
├── 07_pandas_ai/        # AI/ML notebooks
└── docker-compose.yml   # Platform definition
```

### Database Schema Standards
- **raw**: `source_system.table_name` (e.g., `taxi.trips`)
- **staging**: `stg.source_object_purpose` (e.g., `stg.taxi_trips`)
- **marts**: `mart.type_businessname` (e.g., `mart.fct_revenue`)

### Naming Conventions
- **Everything**: snake_case (files, tables, columns)
- **No spaces**: Use underscores
- **Be descriptive**: `calculated_total_amount` not `calc_tot`

## AI Assistant Behavioral Rules

### ALWAYS DO ✅
- Ask which phase the work relates to before starting
- Consider development type impact (Infrastructure/Analytics/Frontend)
- Edit existing files rather than creating new ones
- Use Read tool before any Edit
- Update README.md when changing infrastructure
- Respect the DuckDB single-writer constraint
- Follow established patterns in the codebase
- **CRITICAL**: Follow WSL2 Docker config change protocol (see below)

### NEVER DO ❌
- Create documentation unless explicitly asked
- Write to production (02_duck_db/03_prod/) without approval
- Downgrade software versions
- Create new files when existing ones can be modified
- Assume infrastructure changes are isolated
- Use spaces in filenames or database objects
- Use docker-compose build for config changes in WSL2 (see protocol below)

## WSL2 Docker Configuration Change Protocol 🚨

**PROBLEM**: WSL2 Windows filesystem mounts cause Docker build context issues where config changes don't get picked up, requiring multiple rebuild cycles.

**SOLUTION**: Always use this exact sequence for config changes:

### Step 1: Make Config Change
```bash
# Edit the config file normally
```

### Step 2: Verify Change on Host
```bash
grep -A3 -B3 "YOUR_SETTING" 06_superset/superset_config.py
```

### Step 3: Build with Direct Command (NOT docker-compose)
```bash
docker build --no-cache -t temp-superset-test -f 06_superset/Dockerfile 06_superset
```

### Step 4: Verify Config in Built Image
```bash
docker run --rm temp-superset-test grep -A3 -B3 "YOUR_SETTING" /app/pythonpath/superset_config.py
```

### Step 5: Tag and Deploy
```bash
docker tag temp-superset-test proto_loc-superset:latest
docker-compose stop superset
docker-compose rm -f superset
docker-compose up -d superset
```

### Step 6: Verify Config Loaded in Running Container
```bash
docker-compose exec superset python -c "from superset import config; print('YOUR_SETTING:', config.FEATURE_FLAGS.get('YOUR_SETTING'))"
```

**WHY THIS WORKS**: Direct docker build bypasses WSL2 build context issues that affect docker-compose build.

**TIME SAVINGS**: This protocol ensures config changes work on first try instead of requiring 3-5 rebuild cycles.

## Quick Command Reference

### Check Platform Status
```bash
docker-compose ps
curl http://localhost:3000  # Dagster
curl http://localhost:8088  # Superset
curl http://localhost:4000  # Cube.js
```

### Database Connections
- **Dagster**: Writes to all databases
- **dbt**: Reads raw, writes dev/prod
- **Superset**: Read-only to all databases
- **Cube.js**: Read-only to dev database

## Current Platform State
- **Phase**: 1 (Infrastructure Development) - Transitioning to Phase 2
- **Stability**: Core services stable, feature compatibility issues documented
- **Next Steps**: See Strategic Roadmap below

## Strategic Roadmap - Next Major Initiatives

### **Priority 1: Git Commit Preparation** 🔒
- [ ] Security sweep across full project directory
- [ ] Update .gitignore for any new sensitive patterns
- [ ] Move confidential information to .env files
- [ ] Prepare for public repository commit

### **Priority 2: Cube.dev Validation & Troubleshooting** 📊
- [ ] Verify data models are rendering correctly
- [ ] Investigate missing table joins in UI
- [ ] Confirm actual cube definitions are being created
- [ ] Battle-test semantic layer functionality

### **Priority 3: Dagster Integration Review** ⚙️
- [ ] Review Dagster interactions with DuckDB, Cube.js, dbt
- [ ] Validate expected behaviors vs actual behaviors
- [ ] Identify troubleshooting needs for service quality

### **Priority 4: Cube.dev → Superset Integration** 🔗
- [ ] Understand expected benefits of Cube integration
- [ ] Verify joins are working in Superset visualizations
- [ ] Diagnose configuration gaps vs expected behavior
- [ ] Test vendor name + vendor ID joined visualizations

### **Priority 5: Full Data Pipeline Rebuild** 🔄
- [ ] Clear all DuckDB data for fresh start
- [ ] Recreate Dagster assets from zero
- [ ] Recreate dbt models from zero
- [ ] Recreate Cube.js models from zero
- [ ] Connect to blank Superset + Cube integration
- [ ] Validate complete end-to-end data flow

### **Priority 6: Pandas AI Service Evaluation** 🤖
- [ ] Comprehensive testing of Pandas AI functionality
- [ ] Integration testing with stabilized services
- [ ] Performance and capability assessment

### **Priority 7: Platform Hardening for Production** 🛡️
- [ ] Comprehensive configuration hardening
- [ ] Production-ready security measures
- [ ] Performance optimization and testing
- [ ] Documentation for forkable repository

### **Priority 8: Fork Validation Testing** 🍴
- [ ] Test complete fork process
- [ ] Validate performance with different datasets
- [ ] Confirm all behaviors work as expected
- [ ] Production deployment readiness

## Current Status
**✅ Infrastructure Stable**: Core services operational with documented compatibility issues  
**🎯 Next Focus**: Git security preparation and Cube.dev troubleshooting

## See Also
- `CLAUDE_PHASE1_INFRA.md` - Detailed infrastructure guidelines
- `CLAUDE_PHASE2_ANALYTICS.md` - Analytics development patterns
- `.clinerules/` - Official project rules
- `other/golden_versions_DRAFT.md` - Version management 