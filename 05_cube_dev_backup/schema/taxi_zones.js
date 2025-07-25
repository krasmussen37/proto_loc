/**
 * NYC TLC Taxi Zones Dimension Cube
 * 
 * Official TLC Taxi Zone lookup data with geospatial information.
 * This cube provides geographic context for taxi trip analysis,
 * including zone names, borough classifications, and spatial boundaries.
 * 
 * Data Source: dim_taxi_zones_geospatial (mart layer)
 * Grain: One row per TLC Taxi Zone
 * Update Frequency: Infrequent (zones rarely change)
 */
cube('TaxiZones', {
  sql: 'SELECT * FROM dim_taxi_zones_geospatial',
  
  title: 'NYC TLC Taxi Zones',
  description: 'Official TLC Taxi Zone boundaries and geographic metadata for trip location analysis',

  dimensions: {
    // Primary Zone Identifier
    locationId: {
      sql: 'LocationID',
      type: 'string',
      primaryKey: true,
      title: 'TLC Zone ID',
      description: 'Official TLC Taxi Zone identifier used in trip records'
    },
    
    // Zone Geographic Information
    zoneName: {
      sql: 'Zone',
      type: 'string',
      title: 'Zone Name',
      description: 'Official name of the taxi zone (e.g., Times Square/Theatre District, Central Park, etc.)'
    },
    
    borough: {
      sql: 'Borough',
      type: 'string',
      title: 'NYC Borough',
      description: 'NYC borough containing this zone (Manhattan, Brooklyn, Queens, Bronx, Staten Island, EWR)'
    },
    
    serviceZone: {
      sql: 'service_zone',
      type: 'string',
      title: 'Service Zone Type',
      description: 'TLC service zone classification (Yellow Zone, Green Zone, etc.)'
    },

    // Geospatial Dimensions
    zoneAreaSqMeters: {
      sql: 'zone_area_sq_meters',
      type: 'number',
      title: 'Zone Area (Square Meters)',
      description: 'Geographic area of the taxi zone in square meters',
      format: '#,##0'
    },
    
    centroidLongitude: {
      sql: 'zone_centroid_longitude',
      type: 'number',
      title: 'Centroid Longitude',
      description: 'Longitude coordinate of the zone centroid for mapping',
      format: '#,##0.000000'
    },
    
    centroidLatitude: {
      sql: 'zone_centroid_latitude', 
      type: 'number',
      title: 'Centroid Latitude',
      description: 'Latitude coordinate of the zone centroid for mapping',
      format: '#,##0.000000'
    },

    // Geospatial Data (for advanced use cases)
    geometryWkt: {
      sql: 'geometry_wkt',
      type: 'string',
      title: 'Zone Boundary (WKT)',
      description: 'Well-Known Text representation of zone boundary polygon'
    },
    
    geometryGeoJson: {
      sql: 'geometry_geojson',
      type: 'string', 
      title: 'Zone Boundary (GeoJSON)',
      description: 'GeoJSON representation of zone boundary for web mapping'
    }
  },

  measures: {
    // Zone Counts
    totalZones: {
      type: 'count',
      title: 'Total Zone Count',
      description: 'Number of TLC Taxi Zones'
    },
    
    // Geographic Metrics
    totalCoverageArea: {
      sql: 'zone_area_sq_meters',
      type: 'sum',
      title: 'Total Coverage Area (sq meters)',
      description: 'Total geographic area covered by selected zones',
      format: '#,##0'
    },
    
    avgZoneArea: {
      sql: 'zone_area_sq_meters',
      type: 'avg',
      title: 'Average Zone Area (sq meters)',
      description: 'Average geographic area per zone',
      format: '#,##0'
    }
  },

  preAggregations: {
    // Borough-level summary
    boroughSummary: {
      measures: [totalZones, totalCoverageArea, avgZoneArea],
      dimensions: [borough, serviceZone],
      refreshKey: { every: '24 hours' }
    }
  }
});