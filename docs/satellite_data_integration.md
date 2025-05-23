# Satellite Data Integration Guide

FireSight integrates multiple satellite data sources to provide comprehensive wildfire detection, monitoring, and prediction capabilities. This guide explains the available satellite data sources and how to use them.

## Available Satellite Data Sources

FireSight integrates the following satellite data sources:

| Source | Description | Resolution | Update Frequency | Coverage |
| ------ | ----------- | ---------- | ---------------- | -------- |
| NASA FIRMS | Fire Information for Resource Management System - standard VIIRS data | 375m | 3h - NRT, Daily - SP | Global |
| GOES-16/17 | ABI Fire/Hot-Spot Characterization | 2km | 5-15 min | Americas |
| MODIS Collection 6.1 | MODIS active fire detection product | 1km | 2x daily | Global |
| VIIRS I-Band SNPP | Active fire product from Suomi NPP satellite | 375m | 12h | Global |
| VIIRS I-Band NOAA-20 | Active fire product from NOAA-20 satellite | 375m | 12h | Global |
| Combined VIIRS | Merged product from both SNPP and NOAA-20 | 375m | 12h | Global |
| Sentinel-2 | High-resolution optical imagery | 10-60m | 2-5 days | Global |
| Landsat | Optical and thermal imagery | 30m | 16 days | Global |
| NIFC Perimeters | WFIGS fire perimeter data from NIFC | Vector | Daily | US |
| IRWIN Incidents | Integrated Reporting of Wildfire Information | Point | Daily | US |
| NOAA HRRR | Weather forecasts from High-Resolution Rapid Refresh | 3km | Hourly | US |
| NOAA HMS | Smoke forecasts from Hazard Mapping System | 2km | Daily | US |

## Satellite Data Specifications

### NASA FIRMS
- **Provider**: NASA
- **Sensors**: VIIRS, MODIS
- **Data Format**: CSV, ShapeFile, GeoJSON
- **API Available**: Yes, requires API key
- **Documentation**: [FIRMS Documentation](https://firms.modaps.eosdis.nasa.gov/api/)
- **Key Attributes**: Fire Radiative Power (FRP), confidence, acquisition time

### MODIS Collection 6.1
- **Provider**: NASA
- **Sensors**: MODIS on Terra and Aqua satellites
- **Resolution**: 1km
- **Data Format**: CSV, ShapeFile, GeoJSON
- **API Available**: Yes, uses NASA FIRMS API
- **Documentation**: [MODIS Collection 6 Documentation](https://modis-fire.umd.edu/files/MODIS_C6_Fire_User_Guide_B.pdf)
- **Key Attributes**: Brightness temperature, confidence (0-100), FRP

### VIIRS I-Band (375m)
- **Provider**: NASA/NOAA
- **Platforms**: Suomi NPP and NOAA-20 satellites
- **Resolution**: 375m
- **Data Format**: CSV, ShapeFile, GeoJSON
- **API Available**: Yes, uses NASA FIRMS API
- **Documentation**: [VIIRS I-Band Documentation](https://www.earthdata.nasa.gov/learn/find-data/near-real-time/firms/viirs-i-band-375-m-active-fire-data)
- **Key Attributes**: Higher resolution than MODIS, confidence (nominal/high), FRP

### Combined VIIRS
- **Provider**: NASA/NOAA (through FireSight processing)
- **Platforms**: Merged data from Suomi NPP and NOAA-20
- **Benefits**: Reduced duplicate detections, increased temporal resolution
- **Key Attributes**: Merged confidence scores, detection counts, combined FRP

### GOES ABI Fire Detection
- **Provider**: NOAA
- **Satellites**: GOES-16 (East) and GOES-17 (West)
- **Resolution**: 2km
- **Update Frequency**: 5-15 minutes
- **Documentation**: [GOES Fire Detection](https://www.ospo.noaa.gov/Products/land/hms.html)
- **Key Attributes**: Near real-time detection, continuous monitoring

## Using Satellite Data in FireSight

### Configuration Options

The FireSight platform allows configuring which satellite data sources to use. In the `satellite_coordinator.py` module, you can specify these options:

```python
# Configuration options
config = {
    "lat": 34.05,                  # Center latitude
    "lon": -118.25,                # Center longitude
    "radius_km": 100,              # Search radius
    "days": 1,                     # Days to look back
    "state": "CA",                 # For US state-specific sources
    "goes_hours_back": 6,          # Hours to look back for GOES
    "forecast_hours": 24,          # Weather forecast hours
    "nifc_days_back": 7,           # Days to look back for perimeters
    
    # Enable/disable specific sources
    "use_nasa_firms": True,
    "use_goes": True,
    "use_nifc": True,
    "use_irwin": True,
    "use_modis": True,
    "use_viirs_snpp": True,
    "use_viirs_noaa20": True,
    "use_viirs_combined": True,
    "use_noaa_weather": True,
    
    # API credentials (use environment variables in production)
    "nasa_api_key": "YOUR_API_KEY",
    "aws_access_key": "YOUR_AWS_KEY",
    "aws_secret_key": "YOUR_AWS_SECRET"
}
```

### Ingesting Satellite Data

To ingest data from all configured satellite sources:

```python
from satellite_coordinator import ingest_all_satellite_data

# Define configuration
config = {
    "lat": 37.7, 
    "lon": -119.5,  # Yosemite area
    "radius_km": 100,
    "days": 1,
    "nasa_api_key": "YOUR_API_KEY"
}

# Get data from all sources
satellite_entries = ingest_all_satellite_data(config)

# Check what we got
for source, count in [(e["source"], e["source"]) for e in satellite_entries]:
    print(f"{source}: {count} entries")
```

### Running Comprehensive Analysis

For full wildfire detection and prediction using all data sources:

```python
from satellite_coordinator import run_comprehensive_analysis

# Run in demo mode (uses sample data if APIs unavailable)
results = run_comprehensive_analysis(mode="demo")

# Access results
alerts = results["alerts"]
predictions = results["predictions"]
resources = results["resources"]
data_summary = results["data_summary"]

# Display alert summary
for alert in alerts:
    print(f"Alert: {alert['type']} - Severity: {alert['severity']} - Confidence: {alert['confidence']}")
```

## Testing New Satellite Sources

You can test individual satellite data sources using the test script:

```bash
# Run all tests
python test_satellite_integration.py

# To use a real NASA API key (optional)
export NASA_API_KEY="your_api_key_here"
python test_satellite_integration.py
```

## Data Integration in the Pipeline

The satellite data sources are integrated into the FireSight data pipeline:

1. Data ingestion from multiple satellite sources
2. Conversion to unified data schema
3. Fusion with other data sources (cameras, IoT sensors, weather)
4. Analysis by FireSight analytics engine
5. Fire detection and alert generation
6. Fire spread prediction
7. Resource optimization

## Data Schema

All satellite data is converted to a unified schema:

```json
{
  "source": "satellite_source_name",
  "timestamp": "2023-01-01T12:34:56Z",
  "lat": 34.0522,
  "lon": -118.2437,
  "data": {
    "satellite": "satellite_name",
    "instrument": "instrument_name",
    "confidence": "confidence_value",
    "frp": 25.7,
    "additional_attributes": "source_specific_values"
  }
}
```

This unified schema allows the FireSight system to process data from multiple sources in a consistent manner.
