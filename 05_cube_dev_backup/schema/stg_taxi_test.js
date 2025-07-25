/**
 * Simple Test Cube for Staging Data
 * 
 * Basic model to test Cube.js functionality using staging tables
 * while keeping main semantic models pointed at mart tables.
 */
cube('StagingTaxiTest', {
  sql: 'SELECT * FROM stg_taxi_trips',
  
  title: 'Staging Taxi Test',
  description: 'Simple test cube using staging data',

  dimensions: {
    vendorId: {
      sql: 'VendorID',
      type: 'string',
      title: 'Vendor ID'
    },
    
    pickupZone: {
      sql: 'PULocationID', 
      type: 'string',
      title: 'Pickup Zone'
    },
    
    pickupDate: {
      sql: 'pickup_date',
      type: 'time',
      title: 'Pickup Date'
    }
  },

  measures: {
    tripCount: {
      type: 'count',
      title: 'Trip Count'
    },
    
    avgFare: {
      sql: 'fare_amount',
      type: 'avg',
      title: 'Average Fare',
      format: '$#,##0.00'
    },
    
    totalRevenue: {
      sql: 'total_amount',
      type: 'sum', 
      title: 'Total Revenue',
      format: '$#,##0.00'
    }
  }
});