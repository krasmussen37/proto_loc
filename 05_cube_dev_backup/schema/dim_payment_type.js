/**
 * Payment Type Dimension Cube
 * 
 * Official TLC payment method lookup table. Defines how passengers
 * paid for their taxi trips, including credit cards, cash, and
 * special transaction types.
 * 
 * Data Source: dim_payment_type (mart layer from dbt seed)
 * Grain: One row per payment method
 * Update Frequency: Rare (payment types change infrequently)
 */
cube('PaymentTypeDim', {
  sql: 'SELECT * FROM dim_payment_type',
  
  title: 'Payment Methods',
  description: 'Official TLC payment method classifications',

  dimensions: {
    paymentTypeId: {
      sql: 'payment_type',
      type: 'string',
      primaryKey: true,
      title: 'Payment Type ID',
      description: 'Numeric payment method identifier (0-6)'
    },
    
    paymentName: {
      sql: 'payment_name',
      type: 'string',
      title: 'Payment Method',
      description: 'Human-readable payment method name'
    },
    
    paymentDescription: {
      sql: 'payment_description',
      type: 'string',
      title: 'Payment Description',
      description: 'Detailed description of the payment method'
    }
  },

  measures: {
    paymentMethodCount: {
      type: 'count',
      title: 'Number of Payment Methods',
      description: 'Total number of available payment methods'
    }
  }
});