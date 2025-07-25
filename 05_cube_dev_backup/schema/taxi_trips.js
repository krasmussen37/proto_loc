/**
 * NYC Yellow Taxi Trips Fact Cube
 * 
 * Primary fact table containing all yellow taxi trip transactions with denormalized
 * dimension attributes. Based on TLC's official yellow taxi trip record data.
 * 
 * Data Source: fct_taxi_trips (mart layer)
 * Grain: One row per completed taxi trip
 * Update Frequency: Daily via Dagster pipeline
 */
cube('TaxiTrips', {
  sql: 'SELECT * FROM fct_taxi_trips',
  
  title: 'NYC Yellow Taxi Trips',
  description: 'Official TLC yellow taxi trip records with comprehensive trip, fare, and location data',

  // Define relationships to dimension tables (Star Schema)
  joins: {
    VendorDim: {
      relationship: 'many_to_one',
      sql: `${CUBE}.VendorID = ${VendorDim}.vendor_id`
    },
    
    PaymentTypeDim: {
      relationship: 'many_to_one', 
      sql: `${CUBE}.payment_type = ${PaymentTypeDim}.payment_type`
    },
    
    RateCodeDim: {
      relationship: 'many_to_one',
      sql: `${CUBE}.RatecodeID = ${RateCodeDim}.rate_code_id`
    },
    
    TaxiZones: {
      relationship: 'many_to_one',
      sql: `${CUBE}.PULocationID = ${TaxiZones}.LocationID`,
      alias: 'PickupZone'
    },
    
    // Second join for dropoff zones
    DropoffZone: {
      relationship: 'many_to_one',
      sql: `${CUBE}.DOLocationID = ${TaxiZones}.LocationID`  
    }
  },

  dimensions: {
    // TPEP Provider Information
    vendorId: {
      sql: 'VendorID',
      type: 'string',
      title: 'Vendor ID',
      description: 'TPEP provider code: 1=Creative Mobile Technologies LLC, 2=Curb Mobility LLC, 6=Myle Technologies Inc, 7=Helix'
    },
    
    vendorName: {
      sql: 'vendor_name',
      type: 'string',
      title: 'TPEP Provider',
      description: 'Technology vendor company that provided the trip record'
    },

    // Trip Fare Classification
    rateCodeId: {
      sql: 'RatecodeID',
      type: 'string',
      title: 'Rate Code ID',
      description: 'Final rate code at trip end: 1=Standard, 2=JFK, 3=Newark, 4=Nassau/Westchester, 5=Negotiated, 6=Group ride, 99=Unknown'
    },
    
    rateCodeName: {
      sql: 'rate_code_name',
      type: 'string',
      title: 'Rate Code Type',
      description: 'Human-readable rate code (Standard rate, JFK Airport, Newark Airport, etc.)'
    },

    // Payment Method
    paymentTypeId: {
      sql: 'payment_type',
      type: 'string', 
      title: 'Payment Type ID',
      description: 'Payment method code: 0=Flex Fare, 1=Credit card, 2=Cash, 3=No charge, 4=Dispute, 5=Unknown, 6=Voided trip'
    },
    
    paymentMethod: {
      sql: 'payment_name',
      type: 'string',
      title: 'Payment Method',
      description: 'How passenger paid for the trip (Credit card, Cash, No charge, etc.)'
    },

    // Trip Timing - Official TLC Definitions
    pickupDatetime: {
      sql: 'tpep_pickup_datetime',
      type: 'time',
      title: 'Meter Engagement Time',
      description: 'Date and time when the taximeter was engaged (trip start)'
    },
    
    dropoffDatetime: {
      sql: 'tpep_dropoff_datetime',
      type: 'time',
      title: 'Meter Disengagement Time', 
      description: 'Date and time when the taximeter was disengaged (trip end)'
    },

    // Geographic Dimensions - TLC Taxi Zones
    pickupLocationId: {
      sql: 'PULocationID',
      type: 'string',
      title: 'Pickup Zone ID',
      description: 'TLC Taxi Zone where the taximeter was engaged'
    },
    
    pickupZone: {
      sql: 'pickup_zone',
      type: 'string',
      title: 'Pickup Zone Name',
      description: 'Name of the TLC Taxi Zone where trip originated'
    },
    
    pickupBorough: {
      sql: 'pickup_borough',
      type: 'string',
      title: 'Pickup Borough',
      description: 'NYC borough where taximeter was engaged'
    },
    
    dropoffLocationId: {
      sql: 'DOLocationID',
      type: 'string',
      title: 'Dropoff Zone ID',
      description: 'TLC Taxi Zone where the taximeter was disengaged'
    },
    
    dropoffZone: {
      sql: 'dropoff_zone',
      type: 'string',
      title: 'Dropoff Zone Name',
      description: 'Name of the TLC Taxi Zone where trip ended'
    },
    
    dropoffBorough: {
      sql: 'dropoff_borough',
      type: 'string',
      title: 'Dropoff Borough',
      description: 'NYC borough where taximeter was disengaged'
    },

    // Trip Characteristics
    passengerCount: {
      sql: 'passenger_count',
      type: 'number',
      title: 'Passenger Count',
      description: 'Number of passengers in the vehicle (driver-entered)'
    },
    
    tripDistanceMiles: {
      sql: 'trip_distance',
      type: 'number',
      title: 'Trip Distance (Miles)',
      description: 'Elapsed trip distance in miles as reported by the taximeter',
      format: '#,##0.00'
    },
    
    storeAndForwardFlag: {
      sql: 'store_and_fwd_flag',
      type: 'string',
      title: 'Store and Forward Flag',
      description: 'Y=Trip record held in vehicle memory before transmission, N=Direct transmission to vendor'
    },

    // Calculated Time Dimensions (from mart layer)
    pickupDate: {
      sql: 'pickup_date',
      type: 'time',
      title: 'Pickup Date',
      description: 'Date portion of meter engagement for daily analysis'
    },
    
    pickupHour: {
      sql: 'pickup_hour',
      type: 'number',
      title: 'Pickup Hour (0-23)',
      description: 'Hour of day when meter was engaged for time-of-day patterns'
    },
    
    pickupDayOfWeek: {
      sql: 'pickup_day_of_week',
      type: 'number',
      title: 'Pickup Day of Week',
      description: 'Day of week for pickup (0=Sunday, 1=Monday, etc.)'
    }
  },

  measures: {
    // Trip Volume
    tripCount: {
      type: 'count',
      title: 'Total Trips',
      description: 'Number of completed taxi trips'
    },
    
    totalPassengers: {
      sql: 'passenger_count',
      type: 'sum',
      title: 'Total Passengers',
      description: 'Sum of all passengers across trips'
    },

    // Distance Metrics
    totalMilesTraveled: {
      sql: 'trip_distance',
      type: 'sum',
      title: 'Total Miles Traveled',
      description: 'Total distance in miles as reported by taximeters',
      format: '#,##0.0'
    },
    
    avgTripDistance: {
      sql: 'trip_distance',
      type: 'avg',
      title: 'Average Trip Distance',
      description: 'Average trip distance in miles per trip',
      format: '#,##0.00'
    },

    // Core Fare Revenue (Time and Distance)
    totalFareAmount: {
      sql: 'fare_amount',
      type: 'sum',
      title: 'Total Fare Revenue',
      description: 'Total time-and-distance fare calculated by meters',
      format: '$#,##0.00'
    },
    
    avgFareAmount: {
      sql: 'fare_amount',
      type: 'avg',
      title: 'Average Fare per Trip',
      description: 'Average time-and-distance fare per trip',
      format: '$#,##0.00'
    },

    // Tips (Credit Card Only)
    totalTips: {
      sql: 'tip_amount',
      type: 'sum',
      title: 'Total Tips (Credit Card)',
      description: 'Total tip amount - automatically populated for credit card tips only (cash tips not included)',
      format: '$#,##0.00'
    },
    
    avgTipAmount: {
      sql: 'tip_amount',
      type: 'avg',
      title: 'Average Tip per Trip',
      description: 'Average credit card tip per trip (cash tips not included)',
      format: '$#,##0.00'
    },

    // Total Revenue to Passengers
    totalRevenueCharged: {
      sql: 'total_amount',
      type: 'sum',
      title: 'Total Amount Charged',
      description: 'Total amount charged to passengers (does not include cash tips)',
      format: '$#,##0.00'
    },
    
    avgRevenuePerTrip: {
      sql: 'total_amount',
      type: 'avg',
      title: 'Average Revenue per Trip',
      description: 'Average total amount charged per trip',
      format: '$#,##0.00'
    },

    // Regulatory Taxes and Surcharges
    totalMtaTax: {
      sql: 'mta_tax',
      type: 'sum',
      title: 'Total MTA Tax',
      description: 'Tax automatically triggered based on metered rate in use',
      format: '$#,##0.00'
    },
    
    totalImprovementSurcharge: {
      sql: 'improvement_surcharge',
      type: 'sum',
      title: 'Total Improvement Surcharge',
      description: 'Improvement surcharge assessed at flag drop (started 2015)',
      format: '$#,##0.00'
    },
    
    totalCongestionSurcharge: {
      sql: 'congestion_surcharge',
      type: 'sum',
      title: 'Total NYS Congestion Surcharge',
      description: 'Total amount collected for New York State congestion surcharge',
      format: '$#,##0.00'
    },
    
    totalAirportFees: {
      sql: 'airport_fee',
      type: 'sum',
      title: 'Total Airport Fees',
      description: 'Fees for pickups at LaGuardia and JFK Airports only',
      format: '$#,##0.00'
    },

    // Miscellaneous Revenue
    totalExtrasAndSurcharges: {
      sql: 'extra',
      type: 'sum',
      title: 'Total Extras & Surcharges',
      description: 'Miscellaneous extras and surcharges',
      format: '$#,##0.00'
    },
    
    totalTolls: {
      sql: 'tolls_amount',
      type: 'sum',
      title: 'Total Tolls',
      description: 'Total amount of all tolls paid during trips',
      format: '$#,##0.00'
    },

    // Efficiency Metrics (from mart calculations)
    avgFarePerMile: {
      sql: 'fare_per_mile',
      type: 'avg',
      title: 'Average Fare per Mile',
      description: 'Revenue efficiency: average fare per mile traveled',
      format: '$#,##0.00'
    },
    
    avgTripDurationMinutes: {
      sql: 'trip_duration_minutes',
      type: 'avg',
      title: 'Average Trip Duration',
      description: 'Average time between meter engagement and disengagement',
      format: '#,##0.0 min'
    }
  },

  preAggregations: {
    // Daily operational dashboard
    dailyOperations: {
      measures: [tripCount, totalRevenueCharged, totalMilesTraveled, avgFareAmount],
      dimensions: [pickupDate, pickupBorough, vendorName],
      timeDimension: pickupDatetime,
      granularity: 'day'
    },
    
    // Payment method analysis
    paymentAnalysis: {
      measures: [tripCount, totalRevenueCharged, totalTips, avgTipAmount],
      dimensions: [paymentMethod, pickupBorough],
      refreshKey: { every: '4 hours' }
    },
    
    // Geographic flow analysis
    tripFlow: {
      measures: [tripCount, avgFareAmount, avgTripDistance],
      dimensions: [pickupZone, dropoffZone, pickupBorough, dropoffBorough],
      refreshKey: { every: '6 hours' }
    }
  }
});