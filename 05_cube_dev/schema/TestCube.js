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
