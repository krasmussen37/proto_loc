cube(`raw_taxi_zones`, {
  sql_table: `nyc_taxi_data.raw_taxi_zones`,
  
  data_source: `default`,
  
  joins: {
    
  },
  
  dimensions: {
    borough: {
      sql: `${CUBE}."Borough"`,
      type: `string`
    },
    
    service_zone: {
      sql: `service_zone`,
      type: `string`
    },
    
    zone: {
      sql: `${CUBE}."Zone"`,
      type: `string`
    }
  },
  
  measures: {
    count: {
      type: `count`
    }
  },
  
  pre_aggregations: {
    // Pre-aggregation definitions go here.
    // Learn more in the documentation: https://cube.dev/docs/caching/pre-aggregations/getting-started
  }
});
