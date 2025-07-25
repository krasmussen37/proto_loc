// Enable auto-schema generation for all database tables
cube('fct_taxi_trips', {
  sql: 'SELECT * FROM fct_taxi_trips',
  measures: {
    count: {
      type: 'count'
    }
  }
});