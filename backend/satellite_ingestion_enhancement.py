"""
Enhancement module for FireSight satellite data integration.
This module extends satellite_ingestion.py with additional satellite data sources.
"""

import os
import logging
import requests
import json
import numpy as np
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.satellite.enhancement")

# Import base satellite client classes
from satellite_ingestion import SatelliteDataClient, DEFAULT_TIMEOUT, MAX_RETRIES

class MODISFireClient(SatelliteDataClient):
    """Client for MODIS Collection 6 & 6.1 fire products"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api/area"
    
    def get_active_fires(self, collection="6.1", lat=0, lon=0, radius_km=100, days=1, format="json"):
        """
        Get active fire data from MODIS Collection 6 or 6.1
        
        Args:
            collection: MODIS Collection version ("6" or "6.1")
            lat: Latitude of center point
            lon: Longitude of center point
            radius_km: Search radius in kilometers
            days: Number of days to look back (1-10)
            format: Output format (json, csv, shapefile)
            
        Returns:
            List of fire detections
        """
        logger.info(f"Fetching MODIS Collection {collection} data, {days} days, {lat},{lon} r={radius_km}km")
        
        if not self.api_key:
            logger.warning("MODIS API key not provided - using demo data")
            return self._get_demo_data(lat, lon, collection)
        
        url = f"{self.base_url}/{format}"
        
        # Source is MODIS_NRT (Near Real-Time) or MODIS_SP (Standard Processing)
        source = "MODIS_NRT" if days <= 2 else "MODIS_SP"
        
        params = {
            "source": source,
            "lat": lat,
            "lon": lon, 
            "radius": radius_km,
            "days": days
        }
        
        try:
            response = self._make_request(url, params=params)
            
            if format == "json":
                return response.json()
            elif format == "csv":
                import csv
                from io import StringIO
                reader = csv.DictReader(StringIO(response.text))
                return list(reader)
            else:
                # Return raw content for other formats
                return response.content
                
        except Exception as e:
            logger.error(f"Error fetching MODIS data: {e}")
            return self._get_demo_data(lat, lon, collection)
    
    def _get_demo_data(self, lat, lon, collection="6.1"):
        """Generate sample MODIS fire data for demo purposes"""
        # Create a small grid of points around the center
        points = []
        for i in range(-3, 4, 2):
            for j in range(-3, 4, 2):
                # Skip some points to make it look more realistic
                if abs(i) + abs(j) > 5:
                    continue
                
                # Add some randomness to confidence and FRP
                confidence = np.random.randint(50, 100)
                frp = round(np.random.uniform(5, 45), 1)
                
                # Generate datetime for yesterday with random hour
                dt = datetime.now() - timedelta(days=1)
                dt = dt.replace(hour=np.random.randint(0, 24), minute=np.random.randint(0, 60))
                
                points.append({
                    "latitude": lat + (i * 0.025),
                    "longitude": lon + (j * 0.025),
                    "brightness": round(310 + np.random.normal(0, 5), 1),
                    "scan": round(np.random.uniform(0.5, 1.2), 2),
                    "track": round(np.random.uniform(0.5, 1.2), 2),
                    "acq_date": dt.strftime("%Y-%m-%d"),
                    "acq_time": dt.strftime("%H%M"),  # MODIS uses HHMM format
                    "satellite": "Terra" if np.random.random() > 0.5 else "Aqua",
                    "instrument": "MODIS",
                    "confidence": confidence,
                    "version": f"Collection {collection}",
                    "frp": frp,
                    "daynight": "D" if 6 <= dt.hour <= 18 else "N"
                })
        
        return points


class VIIRSIBandClient(SatelliteDataClient):
    """Client for VIIRS I-Band 375m Active Fire Product"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api/area"
    
    def get_active_fires(self, platform="VIIRS_SNPP", lat=0, lon=0, radius_km=100, days=1, format="json"):
        """
        Get active fire data from VIIRS I-Band 375m
        
        Args:
            platform: Satellite platform ("VIIRS_SNPP" or "VIIRS_NOAA20")
            lat: Latitude of center point
            lon: Longitude of center point
            radius_km: Search radius in kilometers
            days: Number of days to look back (1-10)
            format: Output format (json, csv, shapefile)
            
        Returns:
            List of fire detections
        """
        logger.info(f"Fetching VIIRS I-Band data from {platform}, {days} days, {lat},{lon} r={radius_km}km")
        
        if not self.api_key:
            logger.warning("VIIRS API key not provided - using demo data")
            return self._get_demo_data(lat, lon, platform)
        
        url = f"{self.base_url}/{format}"
        
        # Add _NRT or _SP suffix depending on days
        source = f"{platform}_NRT" if days <= 2 else f"{platform}_SP"
        
        params = {
            "source": source,
            "lat": lat,
            "lon": lon, 
            "radius": radius_km,
            "days": days
        }
        
        try:
            response = self._make_request(url, params=params)
            
            if format == "json":
                return response.json()
            elif format == "csv":
                import csv
                from io import StringIO
                reader = csv.DictReader(StringIO(response.text))
                return list(reader)
            else:
                # Return raw content for other formats
                return response.content
                
        except Exception as e:
            logger.error(f"Error fetching VIIRS I-Band data: {e}")
            return self._get_demo_data(lat, lon, platform)
    
    def _get_demo_data(self, lat, lon, platform="VIIRS_SNPP"):
        """Generate sample VIIRS I-Band fire data for demo purposes"""
        # Create a grid of points around the center (higher resolution than MODIS)
        points = []
        for i in range(-4, 5):
            for j in range(-4, 5):
                # Skip some points to make it look more realistic
                if abs(i) + abs(j) > 5 or np.random.random() > 0.4:
                    continue
                
                # Add some randomness to confidence and FRP
                confidence = np.random.choice(["nominal", "high"], p=[0.3, 0.7])
                frp = round(np.random.uniform(5, 60), 1)
                
                # Generate datetime for yesterday with random hour
                dt = datetime.now() - timedelta(days=1)
                dt = dt.replace(hour=np.random.randint(0, 24), minute=np.random.randint(0, 60))
                
                points.append({
                    "latitude": lat + (i * 0.015),
                    "longitude": lon + (j * 0.015),
                    "bright_ti4": round(320 + np.random.normal(0, 10), 1),
                    "bright_ti5": round(293 + np.random.normal(0, 5), 1),
                    "scan": round(np.random.uniform(0.3, 0.8), 2),
                    "track": round(np.random.uniform(0.3, 0.8), 2),
                    "acq_date": dt.strftime("%Y-%m-%d"),
                    "acq_time": dt.strftime("%H:%M"),
                    "satellite": "NPP" if platform == "VIIRS_SNPP" else "NOAA-20",
                    "instrument": "VIIRS",
                    "confidence": confidence,
                    "version": "2.0NRT",
                    "frp": frp,
                    "type": np.random.randint(0, 3),  # 0=presumed vegetation fire, 1=active volcano, 2=other static land source, 3=offshore
                    "daynight": "D" if 6 <= dt.hour <= 18 else "N"
                })
        
        return points


class SuomiNPPNOAA20CombinedClient(SatelliteDataClient):
    """Client for Suomi NPP/NOAA-20 Combined VIIRS fire products"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        # Use NASA FIRMS API for combined products
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api/area"
        # Initialize individual clients for data merging
        self.viirs_snpp_client = VIIRSIBandClient(api_key, timeout)
        self.viirs_noaa20_client = VIIRSIBandClient(api_key, timeout)
    
    def get_active_fires(self, lat=0, lon=0, radius_km=100, days=1, format="json", merge_duplicates=True):
        """
        Get combined active fire data from both SNPP and NOAA-20 VIIRS sensors
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            radius_km: Search radius in kilometers
            days: Number of days to look back (1-10)
            format: Output format (json, csv, shapefile)
            merge_duplicates: Whether to merge nearby detections from different satellites
            
        Returns:
            List of combined fire detections
        """
        logger.info(f"Fetching combined SNPP/NOAA-20 VIIRS data, {days} days, {lat},{lon} r={radius_km}km")
        
        try:
            # Get data from both platforms
            snpp_data = self.viirs_snpp_client.get_active_fires(
                platform="VIIRS_SNPP", lat=lat, lon=lon, radius_km=radius_km, days=days, format=format
            )
            
            noaa20_data = self.viirs_noaa20_client.get_active_fires(
                platform="VIIRS_NOAA20", lat=lat, lon=lon, radius_km=radius_km, days=days, format=format
            )
            
            # Combine results
            combined_data = snpp_data + noaa20_data
            
            # If requested, merge detections that are likely the same fire
            if merge_duplicates and combined_data:
                return self._merge_nearby_detections(combined_data)
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error fetching combined VIIRS data: {e}")
            return self._get_demo_data(lat, lon)
    
    def _merge_nearby_detections(self, detections, distance_threshold=0.01):
        """
        Merge detections that are likely observing the same fire
        
        Args:
            detections: List of fire detections
            distance_threshold: Maximum distance (degrees) to consider as same fire
            
        Returns:
            List of merged fire detections
        """
        merged = []
        processed = set()
        
        for i, det1 in enumerate(detections):
            if i in processed:
                continue
                
            # Start a new merged cluster
            cluster = [det1]
            processed.add(i)
            
            # Find all nearby detections
            for j, det2 in enumerate(detections):
                if j in processed or j == i:
                    continue
                    
                # Calculate distance
                lat_diff = abs(float(det1["latitude"]) - float(det2["latitude"]))
                lon_diff = abs(float(det1["longitude"]) - float(det2["longitude"]))
                
                # If within threshold, add to cluster
                if lat_diff < distance_threshold and lon_diff < distance_threshold:
                    cluster.append(det2)
                    processed.add(j)
            
            # Create merged detection
            if len(cluster) == 1:
                merged.append(det1)
            else:
                # Average position and other numerical values
                avg_lat = sum(float(d["latitude"]) for d in cluster) / len(cluster)
                avg_lon = sum(float(d["longitude"]) for d in cluster) / len(cluster)
                avg_frp = sum(float(d["frp"]) for d in cluster if "frp" in d) / len(cluster)
                
                # Select most recent timestamp
                timestamps = [(d["acq_date"], d["acq_time"]) for d in cluster]
                most_recent = max(timestamps)
                
                # Select highest confidence
                confidences = [d["confidence"] for d in cluster]
                highest_conf = max(confidences) if isinstance(confidences[0], (int, float)) else \
                              "high" if "high" in confidences else "nominal"
                
                merged_det = {
                    "latitude": round(avg_lat, 6),
                    "longitude": round(avg_lon, 6),
                    "acq_date": most_recent[0],
                    "acq_time": most_recent[1],
                    "confidence": highest_conf,
                    "frp": round(avg_frp, 1),
                    "sources": [d["satellite"] for d in cluster],
                    "detection_count": len(cluster),
                    "daynight": cluster[0]["daynight"]  # Use first detection's day/night flag
                }
                
                merged.append(merged_det)
        
        return merged
    
    def _get_demo_data(self, lat, lon):
        """Generate sample combined VIIRS fire data for demo purposes"""
        # Use both clients to get demo data and merge
        snpp_data = self.viirs_snpp_client._get_demo_data(lat, lon, "VIIRS_SNPP")
        noaa20_data = self.viirs_noaa20_client._get_demo_data(lat, lon, "VIIRS_NOAA20")
        
        # Combine and merge
        combined_data = snpp_data + noaa20_data
        return self._merge_nearby_detections(combined_data)


# Ingestion functions for converting client data into unified schema
def ingest_modis_fires(api_key=None, collection="6.1", lat=0, lon=0, radius_km=100, days=1):
    """
    Ingest MODIS Collection fire data into unified schema
    
    Args:
        api_key: NASA API key
        collection: MODIS Collection version ("6" or "6.1")
        lat: Latitude of center point
        lon: Longitude of center point
        radius_km: Search radius in kilometers
        days: Number of days to look back
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting MODIS Collection {collection} hotspots: {lat},{lon} r={radius_km}km, {days}d")
    
    client = MODISFireClient(api_key=api_key)
    detections = client.get_active_fires(collection=collection, lat=lat, lon=lon, radius_km=radius_km, days=days)
    
    entries = []
    for det in detections:
        # Build timestamp from acquisition date and time
        if "acq_date" in det and "acq_time" in det:
            # Handle MODIS format (HHMM)
            time_str = det["acq_time"]
            if len(time_str) == 4:
                timestamp = f"{det['acq_date']}T{time_str[:2]}:{time_str[2:]}:00Z"
            else:
                timestamp = f"{det['acq_date']}T00:00:00Z"
        else:
            timestamp = datetime.now().isoformat()
        
        entry = {
            "source": f"modis_c{collection.replace('.', '_')}",  # e.g., modis_c6_1
            "timestamp": timestamp,
            "lat": float(det["latitude"]) if "latitude" in det else 0,
            "lon": float(det["longitude"]) if "longitude" in det else 0,
            "data": {
                "satellite": det.get("satellite", "unknown"),
                "instrument": "MODIS",
                "collection": collection,
                "confidence": int(det["confidence"]) if "confidence" in det else 0,
                "frp": float(det["frp"]) if "frp" in det else 0,
                "brightness": float(det["brightness"]) if "brightness" in det else 0,
                "scan": float(det["scan"]) if "scan" in det else 0,
                "track": float(det["track"]) if "track" in det else 0,
                "daynight": det.get("daynight", "U")
            }
        }
        entries.append(entry)
    
    return entries


def ingest_viirs_iband_fires(api_key=None, platform="VIIRS_SNPP", lat=0, lon=0, radius_km=100, days=1):
    """
    Ingest VIIRS I-Band 375m fire data into unified schema
    
    Args:
        api_key: NASA API key
        platform: Satellite platform ("VIIRS_SNPP" or "VIIRS_NOAA20")
        lat: Latitude of center point
        lon: Longitude of center point
        radius_km: Search radius in kilometers
        days: Number of days to look back
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting VIIRS I-Band {platform} hotspots: {lat},{lon} r={radius_km}km, {days}d")
    
    client = VIIRSIBandClient(api_key=api_key)
    detections = client.get_active_fires(platform=platform, lat=lat, lon=lon, radius_km=radius_km, days=days)
    
    entries = []
    for det in detections:
        # Build timestamp from acquisition date and time
        if "acq_date" in det and "acq_time" in det:
            # Handle VIIRS format (HH:MM)
            if ":" in det["acq_time"]:
                timestamp = f"{det['acq_date']}T{det['acq_time']}:00Z"
            # Handle VIIRS format (HHMM)
            else:
                time_str = det["acq_time"]
                if len(time_str) == 4:
                    timestamp = f"{det['acq_date']}T{time_str[:2]}:{time_str[2:]}:00Z"
                else:
                    timestamp = f"{det['acq_date']}T00:00:00Z"
        else:
            timestamp = datetime.now().isoformat()
        
        # Format source based on platform
        source_name = "viirs_snpp" if platform == "VIIRS_SNPP" else "viirs_noaa20"
        
        entry = {
            "source": source_name,
            "timestamp": timestamp,
            "lat": float(det["latitude"]) if "latitude" in det else 0,
            "lon": float(det["longitude"]) if "longitude" in det else 0,
            "data": {
                "satellite": det.get("satellite", platform.replace("VIIRS_", "")),
                "instrument": "VIIRS",
                "confidence": det.get("confidence", "nominal"),
                "frp": float(det["frp"]) if "frp" in det else 0,
                "bright_ti4": float(det["bright_ti4"]) if "bright_ti4" in det else 0,
                "bright_ti5": float(det["bright_ti5"]) if "bright_ti5" in det else 0,
                "scan": float(det["scan"]) if "scan" in det else 0,
                "track": float(det["track"]) if "track" in det else 0,
                "type": int(det["type"]) if "type" in det else 0,
                "daynight": det.get("daynight", "U")
            }
        }
        entries.append(entry)
    
    return entries


def ingest_combined_viirs_fires(api_key=None, lat=0, lon=0, radius_km=100, days=1):
    """
    Ingest combined Suomi NPP/NOAA-20 VIIRS fire data into unified schema
    
    Args:
        api_key: NASA API key
        lat: Latitude of center point
        lon: Longitude of center point
        radius_km: Search radius in kilometers
        days: Number of days to look back
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting combined VIIRS (SNPP+NOAA20) hotspots: {lat},{lon} r={radius_km}km, {days}d")
    
    client = SuomiNPPNOAA20CombinedClient(api_key=api_key)
    detections = client.get_active_fires(lat=lat, lon=lon, radius_km=radius_km, days=days)
    
    entries = []
    for det in detections:
        # Build timestamp from acquisition date and time
        if "acq_date" in det and "acq_time" in det:
            # Handle VIIRS format (HH:MM)
            if ":" in det["acq_time"]:
                timestamp = f"{det['acq_date']}T{det['acq_time']}:00Z"
            # Handle VIIRS format (HHMM)
            else:
                time_str = det["acq_time"]
                if len(time_str) == 4:
                    timestamp = f"{det['acq_date']}T{time_str[:2]}:{time_str[2:]}:00Z"
                else:
                    timestamp = f"{det['acq_date']}T00:00:00Z"
        else:
            timestamp = datetime.now().isoformat()
        
        entry = {
            "source": "viirs_combined",
            "timestamp": timestamp,
            "lat": float(det["latitude"]) if "latitude" in det else 0,
            "lon": float(det["longitude"]) if "longitude" in det else 0,
            "data": {
                "satellites": det.get("sources", ["unknown"]),
                "instrument": "VIIRS",
                "confidence": det.get("confidence", "nominal"),
                "frp": float(det["frp"]) if "frp" in det else 0,
                "detection_count": det.get("detection_count", 1),
                "daynight": det.get("daynight", "U")
            }
        }
        entries.append(entry)
    
    return entries
