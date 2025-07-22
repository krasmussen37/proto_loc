module.exports = {
  contextToAppId: () => 'CUBE_APP',
  contextToOrchestratorId: () => 'CUBE_APP',
  
  // Explicit database type configuration
  dbType: 'duckdb',
  
  // Database configuration
  databaseType: 'duckdb',
  
  driverFactory: () => {
    const { DuckDBDriver } = require('@cubejs-backend/duckdb-driver');
    return new DuckDBDriver({
      database: process.env.DUCKDB_DEV_PATH || '/app/02_duck_db/02_dev/dev.duckdb'
    });
  },

  // Additional configuration to ensure proper initialization
  scheduledRefreshTimer: false,
  
  // Development server settings
  devServer: {
    port: 4000
  }
};
