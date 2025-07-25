cube('TestCube', {
  sql: 'SELECT 1 as id',
  
  measures: {
    count: {
      type: 'count'
    }
  }
});
