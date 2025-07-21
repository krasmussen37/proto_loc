module.exports = {
  contextToAppId: () => 'CUBE_APP',
  contextToOrchestratorId: () => 'CUBE_APP',
  repositoryFactory: ({ securityContext }) => {
    return {
      dataSchemaFiles: () => Promise.resolve([
        {
          fileName: 'schema/cubes.js',
          content: `
cube('TestCube', {
  sql: 'SELECT 1 as id, \'test\' as name',
  
  measures: {
    count: {
      type: 'count'
    }
  },
  
  dimensions: {
    id: {
      sql: 'id',
      type: 'number',
      primaryKey: true
    },
    name: {
      sql: 'name',
      type: 'string'
    }
  }
});
          `
        }
      ])
    };
  },
  
  dbType: 'duckdb',
  driverFactory: () => {
    const { DuckDBDriver } = require('@cubejs-backend/duckdb-driver');
    return new DuckDBDriver({
      database: process.env.DUCKDB_DEV_PATH || '/app/02_duck_db/02_dev/dev.duckdb'
    });
  }
};
