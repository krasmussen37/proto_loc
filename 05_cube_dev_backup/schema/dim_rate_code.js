/**
 * Rate Code Dimension Cube
 * 
 * Official TLC rate code lookup table. Defines the different fare
 * structures used for taxi trips, including standard rates, airport
 * rates, and special negotiated fares.
 * 
 * Data Source: dim_rate_code (mart layer from dbt seed)
 * Grain: One row per rate code type
 * Update Frequency: Rare (rate codes change infrequently)
 */
cube('RateCodeDim', {
  sql: 'SELECT * FROM dim_rate_code',
  
  title: 'Taxi Rate Codes',
  description: 'Official TLC fare rate code classifications',

  dimensions: {
    rateCodeId: {
      sql: 'rate_code_id',
      type: 'string',
      primaryKey: true,
      title: 'Rate Code ID',
      description: 'Rate code identifier (1-6, 99)'
    },
    
    rateCodeName: {
      sql: 'rate_code_name',
      type: 'string',
      title: 'Rate Code Name',
      description: 'Human-readable rate code name'
    },
    
    rateCodeDescription: {
      sql: 'rate_code_description',
      type: 'string',
      title: 'Rate Code Description',
      description: 'Detailed description of when this rate code applies'
    }
  },

  measures: {
    rateCodeCount: {
      type: 'count',
      title: 'Number of Rate Codes',
      description: 'Total number of available rate codes'
    }
  }
});