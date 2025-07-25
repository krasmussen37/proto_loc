cube(`raw_taxi_trips`, {
  sql_table: `nyc_taxi_data.raw_taxi_trips`,
  
  data_source: `default`,
  
  joins: {
    
  },
  
  dimensions: {
    store_and_fwd_flag: {
      sql: `store_and_fwd_flag`,
      type: `string`
    },
    
    tpep_dropoff_datetime: {
      sql: `tpep_dropoff_datetime`,
      type: `time`
    },
    
    tpep_pickup_datetime: {
      sql: `tpep_pickup_datetime`,
      type: `time`
    }
  },
  
  measures: {
    count: {
      type: `count`
    },
    
    fare_amount: {
      sql: `fare_amount`,
      type: `sum`
    },
    
    passenger_count: {
      sql: `passenger_count`,
      type: `sum`
    },
    
    tip_amount: {
      sql: `tip_amount`,
      type: `sum`
    },
    
    tolls_amount: {
      sql: `tolls_amount`,
      type: `sum`
    },
    
    total_amount: {
      sql: `total_amount`,
      type: `sum`
    }
  },
  
  pre_aggregations: {
    // Pre-aggregation definitions go here.
    // Learn more in the documentation: https://cube.dev/docs/caching/pre-aggregations/getting-started
  }
});
