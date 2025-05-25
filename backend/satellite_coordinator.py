"""
FireSight Satellite Data Integration Coordinator

This module orchestrates the integration of multiple satellite data sources
into the FireSight platform for comprehensive wildfire detection.
"""

import os
import logging
import json
from datetime import datetime
import pandas as pd

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Environment variables must be set manually

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.satellite.coordinator")

# Import original ingestion modules
from ingestion import ingest_camera, ingest_satellite, ingest_sensor
from fusion import fuse_streams

# Import advanced ingestion modules
from advanced_ingestion import ingest_rtsp_camera_feed, ingest_nasa_firms_data
from advanced_ingestion import ingest_iot_sensors, ingest_weather_data, ingest_utility_grid_data

# Import base satellite ingestion modules
from satellite_ingestion import (
    ingest_nasa_firms_hotspots,
    ingest_goes_hotspots,
    ingest_nifc_fire_perimeters,
    ingest_irwin_incidents, 
    ingest_hrrr_forecast
)

# Import enhanced satellite ingestion modules
from satellite_ingestion_enhancement import (
    ingest_modis_fires,
    ingest_viirs_iband_fires,
    ingest_combined_viirs_fires
)

# Import analytics and alert modules
from analytics import detect_threats
from advanced_analytics import detect_wildfires_comprehensive, predict_fire_spread, optimize_firefighting_resources
from alert import generate_alerts

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.coordinator")

def ingest_all_satellite_data(config):
    """
    Ingest data from all configured satellite sources
    
    Args:
        config: Configuration dict with API keys and parameters
        
    Returns:
        Combined list of satellite data entries
    """
    all_entries = []
    
    # Set default coordinates if not specified
    lat = config.get("lat", 34.05)
    lon = config.get("lon", -118.25)
    radius_km = config.get("radius_km", 100)
    days = config.get("days", 1)
    
    # NASA FIRMS data (original)
    if config.get("use_nasa_firms", True):
        logger.info("Ingesting NASA FIRMS data")
        try:
            entries = ingest_nasa_firms_hotspots(
                api_key=config.get("nasa_api_key"),
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                days=days
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} NASA FIRMS entries")
        except Exception as e:
            logger.error(f"Error ingesting NASA FIRMS data: {e}")
    
    # GOES data
    if config.get("use_goes", True):
        logger.info("Ingesting GOES hotspot data")
        try:
            entries = ingest_goes_hotspots(
                aws_access_key=config.get("aws_access_key"),
                aws_secret_key=config.get("aws_secret_key"),
                satellite=config.get("goes_satellite", "GOES16"),
                hours_back=config.get("goes_hours_back", 6)
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} GOES entries")
        except Exception as e:
            logger.error(f"Error ingesting GOES data: {e}")
    
    # NIFC Fire perimeters
    if config.get("use_nifc", True):
        logger.info("Ingesting NIFC fire perimeter data")
        try:
            entries = ingest_nifc_fire_perimeters(
                api_key=config.get("nifc_api_key"),
                state=config.get("state"),
                days_back=config.get("nifc_days_back", 7)
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} NIFC entries")
        except Exception as e:
            logger.error(f"Error ingesting NIFC data: {e}")
    
    # IRWIN Incidents
    if config.get("use_irwin", True):
        logger.info("Ingesting IRWIN incident data")
        try:
            entries = ingest_irwin_incidents(
                api_key=config.get("irwin_api_key"),
                state=config.get("state")
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} IRWIN entries")
        except Exception as e:
            logger.error(f"Error ingesting IRWIN data: {e}")
    
    # NEW: MODIS Collection 6.1
    if config.get("use_modis", True):
        logger.info("Ingesting MODIS Collection 6.1 data")
        try:
            entries = ingest_modis_fires(
                api_key=config.get("nasa_api_key"),
                collection=config.get("modis_collection", "6.1"),
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                days=days
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} MODIS entries")
        except Exception as e:
            logger.error(f"Error ingesting MODIS data: {e}")
    
    # NEW: VIIRS I-Band from SNPP
    if config.get("use_viirs_snpp", True):
        logger.info("Ingesting VIIRS I-Band SNPP data")
        try:
            entries = ingest_viirs_iband_fires(
                api_key=config.get("nasa_api_key"),
                platform="VIIRS_SNPP",
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                days=days
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} VIIRS SNPP entries")
        except Exception as e:
            logger.error(f"Error ingesting VIIRS SNPP data: {e}")
    
    # NEW: VIIRS I-Band from NOAA-20
    if config.get("use_viirs_noaa20", True):
        logger.info("Ingesting VIIRS I-Band NOAA-20 data")
        try:
            entries = ingest_viirs_iband_fires(
                api_key=config.get("nasa_api_key"),
                platform="VIIRS_NOAA20",
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                days=days
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} VIIRS NOAA-20 entries")
        except Exception as e:
            logger.error(f"Error ingesting VIIRS NOAA-20 data: {e}")
    
    # NEW: Combined VIIRS from SNPP and NOAA-20
    if config.get("use_viirs_combined", True):
        logger.info("Ingesting combined VIIRS data")
        try:
            entries = ingest_combined_viirs_fires(
                api_key=config.get("nasa_api_key"),
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                days=days
            )
            all_entries.extend(entries)
            logger.info(f"Added {len(entries)} combined VIIRS entries")
        except Exception as e:
            logger.error(f"Error ingesting combined VIIRS data: {e}")
    
    # NOAA HRRR Weather forecast
    if config.get("use_noaa_weather", True):
        logger.info("Ingesting NOAA HRRR weather forecast")
        try:
            entries = ingest_hrrr_forecast(
                aws_access_key=config.get("aws_access_key"),
                aws_secret_key=config.get("aws_secret_key"),
                lat=lat,
                lon=lon,
                forecast_hours=config.get("forecast_hours", 24)
            )
            # Format as data entries
            weather_entries = []
            for hour_data in entries:
                entry = {
                    "source": "noaa_hrrr",
                    "timestamp": hour_data.get("forecast_time", datetime.now().isoformat()),
                    "lat": lat,
                    "lon": lon,
                    "data": hour_data
                }
                weather_entries.append(entry)
            
            all_entries.extend(weather_entries)
            logger.info(f"Added {len(weather_entries)} NOAA HRRR entries")
        except Exception as e:
            logger.error(f"Error ingesting NOAA HRRR data: {e}")
    
    return all_entries

def run_comprehensive_analysis(mode="demo"):
    """
    Run comprehensive wildfire detection and prediction using all data sources
    
    Args:
        mode: "demo" for demo data or "live" for real API data
        
    Returns:
        Dict containing alerts, predictions, and optimized resources
    """
    # Configuration options
    config = {
        "lat": 34.05,                  # Los Angeles area
        "lon": -118.25,
        "radius_km": 100,
        "days": 1,
        "state": "CA",
        "goes_hours_back": 6,
        "forecast_hours": 24,
        "nifc_days_back": 7
    }
    
    if mode == "live":
        # For live mode, use environment variables or a config file for API keys
        config.update({
            "nasa_api_key": os.getenv("NASA_API_KEY"),
            "aws_access_key": os.getenv("AWS_ACCESS_KEY"),
            "aws_secret_key": os.getenv("AWS_SECRET_KEY"),
        })
    
    logger.info(f"Starting FireSight analysis in {mode} mode")
    
    # Ingest data from all sources
    camera_entries = []
    satellite_entries = []
    sensor_entries = []
    weather_entries = []
    
    if mode == "demo":
        # Use demo data files
        logger.info("Using demo data files")
        camera_entries = ingest_camera('data', lat=config["lat"], lon=config["lon"])
        satellite_entries = ingest_satellite('data/satellite_data.csv')
        sensor_entries = ingest_sensor('data/sensor_logs.json')
    else:
        # Use real data from APIs
        logger.info("Using live data from APIs")
        try:
            # Camera data from RTSP
            camera_entries = ingest_rtsp_camera_feed(
                rtsp_url=config.get("rtsp_url", ""),
                lat=config["lat"],
                lon=config["lon"],
                duration_seconds=30
            ) if config.get("rtsp_url") else []
            
            # IoT sensor data
            sensor_entries = ingest_iot_sensors(
                mqtt_broker=config.get("mqtt_broker", "localhost"),
                port=config.get("mqtt_port", 1883),
                topic=config.get("mqtt_topic", "sensors/#")
            ) if config.get("use_mqtt", False) else []
            
            # Weather data
            weather_entries = ingest_weather_data(
                lat=config["lat"],
                lon=config["lon"],
                api_key=config.get("weather_api_key")
            )
        except Exception as e:
            logger.error(f"Error ingesting real-time data: {e}")
    
    # Get satellite data (both in demo and live modes)
    satellite_entries = ingest_all_satellite_data(config)
    
    # Fuse all data streams
    all_entries = camera_entries + satellite_entries + sensor_entries + weather_entries
    fused = fuse_streams(camera_entries, satellite_entries, sensor_entries + weather_entries)
    
    # Count entries by source
    source_counts = {}
    for entry in all_entries:
        src = entry["source"]
        source_counts[src] = source_counts.get(src, 0) + 1
    
    logger.info(f"Data sources: {source_counts}")
    
    # Perform comprehensive detection and analysis
    fire_alerts = detect_wildfires_comprehensive(fused)
    
    # If fires detected, run prediction and resource optimization
    fire_predictions = []
    resources_plan = []
    
    if fire_alerts:
        fire_predictions = predict_fire_spread(fire_alerts, fused)
        resources_plan = optimize_firefighting_resources(fire_predictions)
    
    return {
        "alerts": fire_alerts,
        "predictions": fire_predictions,
        "resources": resources_plan,
        "data_summary": {
            "total_entries": len(all_entries),
            "by_source": source_counts
        }
    }

def demo():
    """Run demo mode with all data sources"""
    results = run_comprehensive_analysis(mode="demo")
    print(json.dumps(results, indent=2))

def main():
    """Main entry point for the application"""
    # Set default mode (can be overridden via environment variable)
    mode = os.getenv("FIRESIGHT_MODE", "demo")
    results = run_comprehensive_analysis(mode=mode)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    alert_count = len(results["alerts"])
    prediction_count = len(results["predictions"])
    print(f"\nAnalysis complete: {alert_count} alerts, {prediction_count} predictions")
    print(f"Results saved to results_{timestamp}.json")
    
    # If any critical alerts, print them
    critical_alerts = [a for a in results["alerts"] if a.get("severity") == "high"]
    if critical_alerts:
        print("\nCRITICAL ALERTS:")
        for alert in critical_alerts:
            lat = alert.get("lat", 0)
            lon = alert.get("lon", 0)
            confidence = alert.get("confidence", 0) * 100
            print(f"- {alert.get('type')} at ({lat:.4f}, {lon:.4f}) - {confidence:.0f}% confidence")

if __name__ == "__main__":
    main()
