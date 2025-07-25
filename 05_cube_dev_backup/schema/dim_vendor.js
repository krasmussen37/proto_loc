/**
 * TPEP Vendor Dimension Cube
 * 
 * Technology vendor lookup table containing official TPEP (Taxi Passenger
 * Enhancement Program) provider information. These are the companies that
 * provide the electronic trip record systems used in NYC taxis.
 * 
 * Data Source: dim_vendor (mart layer from dbt seed)
 * Grain: One row per TPEP vendor
 * Update Frequency: Rare (vendor list changes infrequently)
 */
cube('VendorDim', {
  sql: 'SELECT * FROM dim_vendor',
  
  title: 'TPEP Vendors',
  description: 'Technology vendors providing taxi trip record systems',

  dimensions: {
    vendorId: {
      sql: 'vendor_id',
      type: 'string',
      primaryKey: true,
      title: 'Vendor ID',
      description: 'TPEP vendor identifier (1, 2, 6, 7)'
    },
    
    vendorName: {
      sql: 'vendor_name',
      type: 'string',
      title: 'Vendor Company Name',
      description: 'Official company name of the TPEP provider'
    },
    
    vendorDescription: {
      sql: 'vendor_description',
      type: 'string',
      title: 'Vendor Description',
      description: 'Description of the TPEP provider and their role'
    }
  },

  measures: {
    vendorCount: {
      type: 'count',
      title: 'Number of Vendors',
      description: 'Total number of TPEP vendors'
    }
  }
});