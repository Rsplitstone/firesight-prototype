"""
Test script for the enhanced satellite data integration.
This script validates the new satellite data sources and displays sample output.
"""

import os
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.test")

# Import the new satellite data sources
from satellite_ingestion_enhancement import (
    ingest_modis_fires,
    ingest_viirs_iband_fires,
    ingest_combined_viirs_fires
)

def print_data_summary(entries, title):
    """Print a summary of the data entries"""
    print(f"\n===== {title} =====")
    print(f"Total entries: {len(entries)}")
    
    if not entries:
        print("No data available.")
        return
    
    # Print first entry as sample
    print("\nSample entry:")
    sample = entries[0]
    print(f"Source: {sample['source']}")
    print(f"Timestamp: {sample['timestamp']}")
    print(f"Location: ({sample['lat']}, {sample['lon']})")
    print("Data:")
    for key, value in sample["data"].items():
        print(f"  {key}: {value}")

def test_modis_collection61(lat=34.05, lon=-118.25):
    """Test MODIS Collection 6.1 data integration"""
    logger.info("Testing MODIS Collection 6.1 data integration")
    
    try:
        # Get API key from environment (or use None for demo data)
        api_key = os.getenv("NASA_API_KEY")
        
        # Fetch MODIS fire data
        entries = ingest_modis_fires(
            api_key=api_key,
            collection="6.1",
            lat=lat,
            lon=lon,
            radius_km=100,
            days=1
        )
        
        print_data_summary(entries, "MODIS Collection 6.1 Fire Data")
        
        return entries
        
    except Exception as e:
        logger.error(f"MODIS Collection 6.1 test failed: {e}")
        return []

def test_viirs_iband(lat=34.05, lon=-118.25):
    """Test VIIRS I-Band data integration for both SNPP and NOAA-20"""
    logger.info("Testing VIIRS I-Band data integration")
    
    entries_snpp = []
    entries_noaa20 = []
    
    try:
        # Get API key from environment (or use None for demo data)
        api_key = os.getenv("NASA_API_KEY")
        
        # Fetch SNPP VIIRS data
        entries_snpp = ingest_viirs_iband_fires(
            api_key=api_key,
            platform="VIIRS_SNPP",
            lat=lat,
            lon=lon,
            radius_km=100,
            days=1
        )
        
        print_data_summary(entries_snpp, "VIIRS I-Band (Suomi NPP) Fire Data")
        
        # Fetch NOAA-20 VIIRS data
        entries_noaa20 = ingest_viirs_iband_fires(
            api_key=api_key,
            platform="VIIRS_NOAA20",
            lat=lat,
            lon=lon,
            radius_km=100,
            days=1
        )
        
        print_data_summary(entries_noaa20, "VIIRS I-Band (NOAA-20) Fire Data")
        
    except Exception as e:
        logger.error(f"VIIRS I-Band test failed: {e}")
    
    return entries_snpp, entries_noaa20

def test_combined_viirs(lat=34.05, lon=-118.25):
    """Test combined VIIRS data from both satellites"""
    logger.info("Testing combined VIIRS data integration")
    
    try:
        # Get API key from environment (or use None for demo data)
        api_key = os.getenv("NASA_API_KEY")
        
        # Fetch combined VIIRS data
        entries = ingest_combined_viirs_fires(
            api_key=api_key,
            lat=lat,
            lon=lon,
            radius_km=100,
            days=1
        )
        
        print_data_summary(entries, "Combined VIIRS (SNPP + NOAA-20) Fire Data")
        
        return entries
        
    except Exception as e:
        logger.error(f"Combined VIIRS test failed: {e}")
        return []

def save_test_results(results):
    """Save all test results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"satellite_test_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Test results saved to {filename}")
    print(f"\nTest results saved to {filename}")

def main():
    """Run all satellite data integration tests"""
    print("\nFireSight Enhanced Satellite Data Integration Test")
    print("=================================================\n")
    
    # Use California wildfires area as test location
    test_lat = 34.05  # Los Angeles area
    test_lon = -118.25
    
    # Run tests for all new data sources
    modis_entries = test_modis_collection61(test_lat, test_lon)
    viirs_snpp_entries, viirs_noaa20_entries = test_viirs_iband(test_lat, test_lon)
    combined_viirs_entries = test_combined_viirs(test_lat, test_lon)
    
    # Summarize results
    total_entries = (len(modis_entries) + len(viirs_snpp_entries) + 
                     len(viirs_noaa20_entries) + len(combined_viirs_entries))
    
    print("\n=================================================")
    print(f"Total fire detections across all sources: {total_entries}")
    print("\nBreakdown by source:")
    print(f"- MODIS Collection 6.1: {len(modis_entries)} detections")
    print(f"- VIIRS I-Band (SNPP): {len(viirs_snpp_entries)} detections")
    print(f"- VIIRS I-Band (NOAA-20): {len(viirs_noaa20_entries)} detections")
    print(f"- Combined VIIRS: {len(combined_viirs_entries)} detections")
    
    # Save all results to a file
    results = {
        "modis": modis_entries,
        "viirs_snpp": viirs_snpp_entries,
        "viirs_noaa20": viirs_noaa20_entries,
        "viirs_combined": combined_viirs_entries,
        "summary": {
            "total": total_entries,
            "modis_count": len(modis_entries),
            "viirs_snpp_count": len(viirs_snpp_entries),
            "viirs_noaa20_count": len(viirs_noaa20_entries),
            "viirs_combined_count": len(combined_viirs_entries)
        }
    }
    save_test_results(results)

if __name__ == "__main__":
    main()
