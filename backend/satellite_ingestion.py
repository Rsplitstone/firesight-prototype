"""
Satellite and weather data ingestion module for FireSight.
Implements connectors for various remote sensing and meteorological data sources.
"""

import os
import io
import boto3
import requests
import json
import logging
import zipfile
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.satellite")

try:
    # Optional dependencies for GeoTIFF/GRIB processing
    # These will be used when available but the module can still function without them
    import rasterio
    import xarray as xr
    import netCDF4
    HAS_GEO_LIBS = True
except ImportError:
    logger.warning("Geospatial libraries not available. Some functionality will be limited.")
    HAS_GEO_LIBS = False

# Constants
DEFAULT_TIMEOUT = 30  # Default timeout for API requests in seconds
MAX_RETRIES = 3  # Maximum number of retry attempts for failed requests


class SatelliteDataClient:
    """Base class for satellite data clients"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.timeout = timeout
    
    def _make_request(self, url, params=None, headers=None, method="GET", retries=MAX_RETRIES):
        """Make an HTTP request with retry logic"""
        if headers is None:
            headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        attempt = 0
        while attempt < retries:
            try:
                if method.upper() == "GET":
                    response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = requests.post(url, json=params, headers=headers, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt >= retries:
                    logger.error(f"Request failed after {retries} attempts: {e}")
                    raise
                logger.warning(f"Request attempt {attempt} failed, retrying: {e}")
        
        return None  # This should not be reached due to the raise in the except block


class NASAFIRMSClient(SatelliteDataClient):
    """Client for NASA FIRMS (Fire Information for Resource Management System)"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api"
    
    def get_active_fires(self, source="VIIRS_SNPP_NRT", lat=0, lon=0, radius_km=100, days=1, format="json"):
        """
        Get active fire data from NASA FIRMS
        
        Args:
            source: Data source (VIIRS_SNPP_NRT, MODIS_NRT, etc.)
            lat: Latitude of center point
            lon: Longitude of center point
            radius_km: Search radius in kilometers
            days: Number of days to look back (1-10)
            format: Output format (json, csv, shapefile)
            
        Returns:
            List of fire detections
        """
        logger.info(f"Fetching NASA FIRMS data: {source}, {days} days, {lat},{lon} r={radius_km}km")
        
        if not self.api_key:
            logger.warning("NASA FIRMS API key not provided - using demo data")
            return self._get_demo_data(lat, lon)
        
        url = f"{self.base_url}/area/{format}"
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
                # Parse CSV data
                import csv
                from io import StringIO
                reader = csv.DictReader(StringIO(response.text))
                return list(reader)
            else:
                # Return raw content for other formats
                return response.content
                
        except Exception as e:
            logger.error(f"Error fetching FIRMS data: {e}")
            return self._get_demo_data(lat, lon)
    
    def _get_demo_data(self, lat, lon):
        """Generate sample FIRMS data for demo purposes"""
        # Create a small grid of points around the center
        points = []
        for i in range(-2, 3):
            for j in range(-2, 3):
                # Skip some points to make it look more realistic
                if abs(i) + abs(j) > 3:
                    continue
                
                # Add some randomness to confidence and FRP
                confidence = np.random.choice(["nominal", "high"], p=[0.3, 0.7])
                frp = round(np.random.uniform(5, 50), 1)
                
                # Generate datetime for yesterday with random hour
                dt = datetime.now() - timedelta(days=1)
                dt = dt.replace(hour=np.random.randint(0, 24), minute=np.random.randint(0, 60))
                
                points.append({
                    "latitude": lat + (i * 0.02),
                    "longitude": lon + (j * 0.02),
                    "bright_ti4": round(320 + np.random.normal(0, 10), 1),
                    "scan": round(np.random.uniform(0.3, 0.8), 2),
                    "track": round(np.random.uniform(0.3, 0.8), 2),
                    "acq_date": dt.strftime("%Y-%m-%d"),
                    "acq_time": dt.strftime("%H:%M"),
                    "satellite": "NPP",
                    "instrument": "VIIRS",
                    "confidence": confidence,
                    "version": "2.0NRT",
                    "frp": frp,
                    "daynight": "D" if 6 <= dt.hour <= 18 else "N"
                })
        
        return points


class GOESHotspotClient(SatelliteDataClient):
    """Client for GOES-16/17 ABI Fire/Hot-Spot data from AWS S3"""
    
    def __init__(self, aws_access_key=None, aws_secret_key=None):
        super().__init__()
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        
        # Initialize AWS S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            # If keys are None, boto3 will use environment variables or IAM role
        )
    
    def get_latest_hotspots(self, satellite="GOES16", hours_back=1):
        """
        Get the latest fire hotspot data from GOES satellite
        
        Args:
            satellite: GOES satellite to use (GOES16 or GOES17)
            hours_back: Number of hours to look back
            
        Returns:
            List of hotspot detections
        """
        logger.info(f"Fetching {satellite} hotspot data from S3, {hours_back}h lookback")
        
        try:
            # In a real implementation, we would:
            # 1. List objects in the appropriate S3 bucket/prefix
            # 2. Find the latest file(s) within our time window
            # 3. Download and parse the file(s)
            
            # For demo purposes, we'll return simulated data:
            return self._get_demo_data(satellite)
            
        except Exception as e:
            logger.error(f"Error fetching GOES data: {e}")
            return self._get_demo_data(satellite)
    
    def _get_demo_data(self, satellite):
        """Generate sample GOES hotspot data for demo purposes"""
        # Demo data focused on western US
        base_lat, base_lon = 37.7, -119.5  # Yosemite area
        
        # Generate 10-20 hotspots
        num_spots = np.random.randint(10, 21)
        hotspots = []
        
        now = datetime.now()
        
        for i in range(num_spots):
            # Random position near base coordinates
            lat = base_lat + np.random.uniform(-1.5, 1.5)
            lon = base_lon + np.random.uniform(-1.5, 1.5)
            
            # Random time in the last hour
            minutes_ago = np.random.randint(5, 60)
            detect_time = now - timedelta(minutes=minutes_ago)
            
            # Random temperature (K) and area
            temp_k = np.random.uniform(320, 450)
            area_km2 = np.random.uniform(0.02, 0.5)
            
            hotspots.append({
                "satellite": satellite,
                "detection_time": detect_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "temp_k": round(temp_k, 1),
                "area_km2": round(area_km2, 4),
                "mask_flag": np.random.randint(0, 2),  # 0 or 1
                "algorithm": "GOES-ABI-Fire",
                "confidence": round(np.random.uniform(0.7, 0.99), 2)
            })
        
        return hotspots


class SentinelClient(SatelliteDataClient):
    """Client for Copernicus Sentinel-2 data"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        self.base_url = "https://services.sentinel-hub.com"
    
    def search_images(self, lat, lon, date_from, date_to, cloud_cover_max=20):
        """
        Search for Sentinel-2 imagery
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            cloud_cover_max: Maximum cloud cover percentage
            
        Returns:
            List of image metadata
        """
        logger.info(f"Searching Sentinel-2 images: {lat},{lon} from {date_from} to {date_to}")
        
        # For demo purposes, return simulated results
        return self._get_demo_data(lat, lon, date_from, date_to)
    
    def get_image(self, image_id, bands=["B04", "B03", "B02"]):
        """
        Get Sentinel-2 image data
        
        Args:
            image_id: ID of the image to retrieve
            bands: List of band names to retrieve
            
        Returns:
            Image data
        """
        logger.info(f"Fetching Sentinel-2 image: {image_id}, bands: {bands}")
        
        # For demo purposes, return None to indicate image download would happen here
        return None
    
    def _get_demo_data(self, lat, lon, date_from, date_to):
        """Generate sample Sentinel-2 image metadata for demo purposes"""
        # Generate 3-5 image results
        num_images = np.random.randint(3, 6)
        images = []
        
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
        
        for i in range(num_images):
            # Random date within range
            days_range = (end_date - start_date).days
            if days_range <= 0:
                days_range = 1
            random_days = np.random.randint(0, days_range)
            image_date = start_date + timedelta(days=random_days)
            
            # Random cloud cover
            cloud_cover = np.random.uniform(0, 20)
            
            images.append({
                "id": f"S2A_MSIL2A_{image_date.strftime('%Y%m%d')}_{np.random.randint(100000, 999999)}",
                "timestamp": image_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "latitude": lat,
                "longitude": lon,
                "cloud_cover_percentage": round(cloud_cover, 1),
                "available_bands": ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"],
                "resolution_m": 10,
                "tile_id": f"{np.random.randint(10, 99)}UXV",
                "orbit_number": np.random.randint(10000, 30000)
            })
        
        return sorted(images, key=lambda x: x["timestamp"], reverse=True)


class LandsatClient(SatelliteDataClient):
    """Client for Landsat 9 Collection 2 data from AWS"""
    
    def __init__(self, aws_access_key=None, aws_secret_key=None):
        super().__init__()
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        
        # Initialize AWS S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            # If keys are None, boto3 will use environment variables or IAM role
        )
    
    def search_scenes(self, lat, lon, date_from, date_to, cloud_cover_max=20):
        """
        Search for Landsat scenes
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            cloud_cover_max: Maximum cloud cover percentage
            
        Returns:
            List of scene metadata
        """
        logger.info(f"Searching Landsat scenes: {lat},{lon} from {date_from} to {date_to}")
        
        # For demo purposes, return simulated results
        return self._get_demo_data(lat, lon, date_from, date_to)
    
    def get_scene_files(self, scene_id, bands=["B4", "B3", "B2"]):
        """
        Get Landsat scene files
        
        Args:
            scene_id: ID of the scene to retrieve
            bands: List of band names to retrieve
            
        Returns:
            Dictionary of band files
        """
        logger.info(f"Fetching Landsat scene: {scene_id}, bands: {bands}")
        
        # For demo purposes, return None
        return None
    
    def _get_demo_data(self, lat, lon, date_from, date_to):
        """Generate sample Landsat scene metadata for demo purposes"""
        # Generate 2-4 scene results
        num_scenes = np.random.randint(2, 5)
        scenes = []
        
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
        
        for i in range(num_scenes):
            # Random date within range
            days_range = (end_date - start_date).days
            if days_range <= 0:
                days_range = 1
            random_days = np.random.randint(0, days_range)
            scene_date = start_date + timedelta(days=random_days)
            
            # Random path/row
            path = np.random.randint(1, 233)
            row = np.random.randint(1, 248)
            
            # Random cloud cover
            cloud_cover = np.random.uniform(0, 20)
            
            scenes.append({
                "id": f"LC09_L2SP_{path:03d}{row:03d}_{scene_date.strftime('%Y%m%d')}_{np.random.randint(1000, 9999)}",
                "timestamp": scene_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "latitude": lat,
                "longitude": lon,
                "cloud_cover_percentage": round(cloud_cover, 1),
                "path": path,
                "row": row,
                "available_bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11"],
                "resolution_m": 30
            })
        
        return sorted(scenes, key=lambda x: x["timestamp"], reverse=True)


class NIFCPerimetersClient(SatelliteDataClient):
    """Client for NIFC Fire Perimeters data"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        self.base_url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_to_Date/FeatureServer/0/query"
    
    def get_current_perimeters(self, state=None, days_back=7):
        """
        Get current fire perimeters
        
        Args:
            state: State filter (e.g., 'CA', 'OR')
            days_back: Number of days to look back
            
        Returns:
            List of fire perimeter data
        """
        logger.info(f"Fetching NIFC fire perimeters: state={state}, {days_back} days back")
        
        start_date = datetime.now() - timedelta(days=days_back)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        params = {
            "where": f"FireDiscoveryDateTime >= '{start_date_str}'",
            "outFields": "*",
            "outSR": "4326",  # WGS84
            "f": "json"
        }
        
        # Add state filter if provided
        if state:
            params["where"] += f" AND POOState = '{state}'"
        
        try:
            response = self._make_request(self.base_url, params=params)
            data = response.json()
            
            # Extract features
            if "features" in data:
                return data["features"]
            else:
                return self._get_demo_data(state)
                
        except Exception as e:
            logger.error(f"Error fetching NIFC perimeters: {e}")
            return self._get_demo_data(state)
    
    def _get_demo_data(self, state=None):
        """Generate sample NIFC fire perimeter data for demo purposes"""
        states = ["CA", "OR", "WA", "ID", "MT", "AZ", "NM", "CO", "UT", "NV"]
        if state:
            states = [state]
        
        # Generate 5-10 fire perimeters
        num_fires = np.random.randint(5, 11)
        perimeters = []
        
        now = datetime.now()
        
        for i in range(num_fires):
            # Random state from list
            fire_state = np.random.choice(states)
            
            # Base coordinates by state (rough centers)
            state_coords = {
                "CA": (37.5, -121.0),
                "OR": (44.0, -121.5),
                "WA": (47.5, -122.0),
                "ID": (45.0, -115.0),
                "MT": (47.0, -110.0),
                "AZ": (34.5, -111.5),
                "NM": (34.0, -106.0),
                "CO": (39.0, -105.5),
                "UT": (39.5, -111.5),
                "NV": (39.5, -117.0)
            }
            
            base_lat, base_lon = state_coords.get(fire_state, (40.0, -120.0))
            
            # Random position near base coordinates
            lat = base_lat + np.random.uniform(-1.0, 1.0)
            lon = base_lon + np.random.uniform(-1.0, 1.0)
            
            # Random time in the last week
            days_ago = np.random.randint(0, 7)
            hours_ago = np.random.randint(0, 24)
            fire_time = now - timedelta(days=days_ago, hours=hours_ago)
            
            # Random fire size (acres)
            fire_size = np.random.uniform(10, 50000)
            if fire_size > 10000:
                fire_size = fire_size * 5  # Make some fires much larger
            
            # Random perimeter coordinates (simplified circle for demo)
            # In a real implementation, this would be a proper GeoJSON polygon
            radius_deg = np.sqrt(fire_size / 250000)  # Very rough conversion from acres to degrees
            
            perimeters.append({
                "attributes": {
                    "OBJECTID": i + 1,
                    "GlobalID": f"{np.random.randint(1000000000, 9999999999)}",
                    "FireYear": now.year,
                    "DiscoveryAcres": round(fire_size, 2),
                    "CalculatedAcres": round(fire_size, 2),
                    "FireDiscoveryDateTime": int(fire_time.timestamp() * 1000),
                    "FireName": f"{np.random.choice(['Cedar', 'Pine', 'Oak', 'Ridge', 'Canyon', 'Mountain', 'Valley'])} Fire",
                    "POOState": fire_state,
                    "POOCounty": f"{np.random.choice(['County', 'Lake', 'Mountains', 'Valley'])}",
                    "FireCause": np.random.choice(["Human", "Natural", "Unknown"], p=[0.4, 0.4, 0.2]),
                    "FireStatus": np.random.choice(["Active", "Contained", "Controlled"], p=[0.6, 0.3, 0.1])
                },
                "geometry": {
                    "rings": [[[lon + radius_deg * np.cos(a), lat + radius_deg * np.sin(a)] for a in np.linspace(0, 2*np.pi, 20)]],
                    "type": "polygon"
                }
            })
        
        return perimeters


class IRWINIncidentsClient(SatelliteDataClient):
    """Client for IRWIN (Integrated Reporting of Wildfire Information) incidents"""
    
    def __init__(self, api_key=None, timeout=DEFAULT_TIMEOUT):
        super().__init__(api_key, timeout)
        self.base_url = "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/IRWIN_to_Inciweb_View/FeatureServer/0/query"
    
    def get_active_incidents(self, state=None):
        """
        Get active wildfire incidents
        
        Args:
            state: State filter (e.g., 'CA', 'OR')
            
        Returns:
            List of incident data
        """
        logger.info(f"Fetching IRWIN incidents: state={state}")
        
        params = {
            "where": "ModifiedOnDateTime_dt > CURRENT_TIMESTAMP - INTERVAL '14' DAY",
            "outFields": "*",
            "outSR": "4326",  # WGS84
            "f": "json"
        }
        
        # Add state filter if provided
        if state:
            params["where"] += f" AND POOState = '{state}'"
        
        try:
            response = self._make_request(self.base_url, params=params)
            data = response.json()
            
            # Extract features
            if "features" in data:
                return data["features"]
            else:
                return self._get_demo_data(state)
                
        except Exception as e:
            logger.error(f"Error fetching IRWIN incidents: {e}")
            return self._get_demo_data(state)
    
    def _get_demo_data(self, state=None):
        """Generate sample IRWIN incident data for demo purposes"""
        states = ["CA", "OR", "WA", "ID", "MT", "AZ", "NM", "CO", "UT", "NV"]
        if state:
            states = [state]
        
        # Generate 8-15 incidents
        num_incidents = np.random.randint(8, 16)
        incidents = []
        
        now = datetime.now()
        
        for i in range(num_incidents):
            # Random state from list
            inc_state = np.random.choice(states)
            
            # Base coordinates by state (rough centers)
            state_coords = {
                "CA": (37.5, -121.0),
                "OR": (44.0, -121.5),
                "WA": (47.5, -122.0),
                "ID": (45.0, -115.0),
                "MT": (47.0, -110.0),
                "AZ": (34.5, -111.5),
                "NM": (34.0, -106.0),
                "CO": (39.0, -105.5),
                "UT": (39.5, -111.5),
                "NV": (39.5, -117.0)
            }
            
            base_lat, base_lon = state_coords.get(inc_state, (40.0, -120.0))
            
            # Random position near base coordinates
            lat = base_lat + np.random.uniform(-1.0, 1.0)
            lon = base_lon + np.random.uniform(-1.0, 1.0)
            
            # Random time in the last week
            days_ago = np.random.randint(0, 14)
            hours_ago = np.random.randint(0, 24)
            inc_time = now - timedelta(days=days_ago, hours=hours_ago)
            
            # Random fire size (acres)
            fire_size = np.random.uniform(10, 50000)
            if fire_size > 10000:
                fire_size = fire_size * 5  # Make some fires much larger
            
            # Resources assigned
            engines = np.random.randint(0, 50)
            helicopters = np.random.randint(0, 10)
            dozers = np.random.randint(0, 15)
            crews = np.random.randint(0, 20)
            personnel = engines * 4 + helicopters * 6 + dozers * 2 + crews * 20
            
            incidents.append({
                "attributes": {
                    "OBJECTID": i + 1,
                    "IrwinID": f"{np.random.randint(10000000, 99999999)}",
                    "IncidentName": f"{np.random.choice(['Cedar', 'Pine', 'Oak', 'Ridge', 'Canyon', 'Mountain', 'Valley'])} Fire",
                    "IncidentTypeCategory": "WF",
                    "InitialResponseAcres": round(fire_size, 2),
                    "DailyAcres": round(fire_size, 2),
                    "PercentContained": np.random.randint(0, 101),
                    "FireCause": np.random.choice(["Human", "Natural", "Unknown"], p=[0.4, 0.4, 0.2]),
                    "FireDiscoveryDateTime": int(inc_time.timestamp() * 1000),
                    "ModifiedOnDateTime_dt": int((inc_time + timedelta(hours=np.random.randint(1, 24))).timestamp() * 1000),
                    "POOState": inc_state,
                    "POOCounty": f"{np.random.choice(['County', 'Lake', 'Mountains', 'Valley'])}",
                    "IncidentStatusCode": np.random.choice(["Active", "Contained", "Controlled"], p=[0.6, 0.3, 0.1]),
                    "TotalIncidentPersonnel": personnel,
                    "TotalIncidentEngines": engines,
                    "TotalIncidentHelicopters": helicopters,
                    "TotalIncidentCrews": crews
                },
                "geometry": {
                    "x": lon,
                    "y": lat,
                    "type": "point"
                }
            })
        
        return incidents


class NOAAWeatherClient(SatelliteDataClient):
    """Client for NOAA HRRR weather data and HMS smoke products"""
    
    def __init__(self, aws_access_key=None, aws_secret_key=None, api_key=None):
        super().__init__(api_key)
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        
        # Initialize AWS S3 client for HRRR data
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            # If keys are None, boto3 will use environment variables or IAM role
        )
    
    def get_hrrr_forecast(self, lat, lon, forecast_hours=24):
        """
        Get HRRR weather forecast for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            forecast_hours: Number of forecast hours to retrieve
            
        Returns:
            Hourly forecast data
        """
        logger.info(f"Fetching HRRR forecast for {lat},{lon}, {forecast_hours}h")
        
        # For demo purposes, generate synthetic forecast
        return self._get_demo_forecast(lat, lon, forecast_hours)
    
    def get_smoke_forecast(self, lat, lon, radius_km=200):
        """
        Get HMS smoke forecast for an area
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            radius_km: Radius in kilometers
            
        Returns:
            Smoke forecast data
        """
        logger.info(f"Fetching HMS smoke forecast for {lat},{lon}, r={radius_km}km")
        
        # For demo purposes, generate synthetic smoke data
        return self._get_demo_smoke(lat, lon, radius_km)
    
    def _get_demo_forecast(self, lat, lon, hours):
        """Generate sample HRRR forecast data for demo purposes"""
        # Generate hourly data for the specified number of hours
        forecast = []
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # Base values for the location
        temp_base = 25  # °C
        if lat > 45:
            temp_base -= 5
        elif lat < 35:
            temp_base += 5
        
        humid_base = 50  # %
        wind_speed_base = 10  # km/h
        wind_dir_base = 270  # degrees (west)
        
        for i in range(hours):
            # Time for this forecast step
            forecast_time = now + timedelta(hours=i)
            
            # Temperature varies by time of day (cooler at night, warmer during day)
            hour_of_day = forecast_time.hour
            time_factor = np.sin(np.pi * (hour_of_day - 4) / 12)  # Peak at 4pm
            temp = temp_base + 8 * time_factor + np.random.normal(0, 1)
            
            # Humidity inverse to temperature
            humid = humid_base - 20 * time_factor + np.random.normal(0, 3)
            humid = max(10, min(95, humid))  # Clamp to reasonable range
            
            # Wind varies somewhat randomly
            wind_speed = wind_speed_base + np.random.normal(0, 3)
            wind_speed = max(0, wind_speed)
            wind_dir = (wind_dir_base + np.random.normal(0, 20)) % 360
            
            # Precipitation (mostly zero, occasional light rain)
            precip = 0
            if np.random.random() < 0.1:  # 10% chance of rain
                precip = np.random.exponential(0.5)
            
            forecast.append({
                "forecast_time": forecast_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "temperature_c": round(temp, 1),
                "humidity_percent": round(humid, 1),
                "wind_speed_kmh": round(wind_speed, 1),
                "wind_direction_deg": round(wind_dir, 0),
                "precipitation_mm": round(precip, 2),
                "pressure_hpa": round(1013.25 + np.random.normal(0, 2), 1),
                "cloud_cover_percent": round(max(0, min(100, 30 + np.random.normal(0, 20))), 0)
            })
        
        return forecast
    
    def _get_demo_smoke(self, lat, lon, radius_km):
        """Generate sample HMS smoke data for demo purposes"""
        # Generate a few smoke plumes in the area
        num_plumes = np.random.randint(0, 4)  # 0-3 plumes
        plumes = []
        
        now = datetime.now()
        
        for i in range(num_plumes):
            # Random position within radius
            distance = np.random.uniform(0, radius_km * 0.8)
            angle = np.random.uniform(0, 2 * np.pi)
            # Approximate degrees for the given distance
            lat_offset = distance / 111  # Rough conversion of km to degrees
            lon_offset = distance / (111 * np.cos(np.radians(lat)))
            
            plume_lat = lat + lat_offset * np.cos(angle)
            plume_lon = lon + lon_offset * np.sin(angle)
            
            # Area and intensity
            area_km2 = np.random.uniform(10, 500)
            intensity = np.random.choice(["Light", "Medium", "Heavy"], p=[0.5, 0.3, 0.2])
            
            # Start/end time
            start_time = now - timedelta(hours=np.random.randint(0, 48))
            duration_hours = np.random.randint(6, 72)
            end_time = start_time + timedelta(hours=duration_hours)
            
            plumes.append({
                "plume_id": f"HMS_{now.strftime('%Y%m%d')}_{i+1}",
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "latitude": plume_lat,
                "longitude": plume_lon,
                "area_km2": round(area_km2, 2),
                "intensity": intensity,
                "source_fire_id": f"FIRE_{np.random.randint(10000, 99999)}",
                "smoke_height_m": round(np.random.uniform(500, 3000)),
                "confidence": np.random.choice(["Low", "Medium", "High"], p=[0.2, 0.5, 0.3])
            })
        
        return plumes


# Ingestion functions for converting the above client data into unified schema
def ingest_nasa_firms_hotspots(api_key=None, lat=0, lon=0, radius_km=100, days=1):
    """
    Ingest NASA FIRMS hotspot data into unified schema
    
    Args:
        api_key: NASA API key
        lat: Latitude of center point
        lon: Longitude of center point
        radius_km: Search radius in kilometers
        days: Number of days to look back
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting NASA FIRMS hotspots: {lat},{lon} r={radius_km}km, {days}d")
    
    client = NASAFIRMSClient(api_key=api_key)
    detections = client.get_active_fires(lat=lat, lon=lon, radius_km=radius_km, days=days)
    
    entries = []
    for det in detections:
        # Build timestamp from acquisition date and time
        if "acq_date" in det and "acq_time" in det:
            # Handle VIIRS format (HH:MM)
            if ":" in det["acq_time"]:
                timestamp = f"{det['acq_date']}T{det['acq_time']}:00Z"
            # Handle MODIS format (HHMM)
            else:
                time_str = det["acq_time"]
                if len(time_str) == 4:
                    timestamp = f"{det['acq_date']}T{time_str[:2]}:{time_str[2:]}:00Z"
                else:
                    timestamp = f"{det['acq_date']}T00:00:00Z"
        else:
            timestamp = datetime.now().isoformat()
        
        entry = {
            "source": "nasa_firms",
            "timestamp": timestamp,
            "lat": float(det["latitude"]) if "latitude" in det else 0,
            "lon": float(det["longitude"]) if "longitude" in det else 0,
            "data": {
                "satellite": det.get("satellite", "unknown"),
                "confidence": det.get("confidence", "nominal"),
                "frp": float(det["frp"]) if "frp" in det else 0,
                "bright_ti4": float(det["bright_ti4"]) if "bright_ti4" in det else 0,
                "bright_ti5": float(det["bright_ti5"]) if "bright_ti5" in det else 0,
                "scan": float(det["scan"]) if "scan" in det else 0,
                "track": float(det["track"]) if "track" in det else 0,
                "daynight": det.get("daynight", "U")
            }
        }
        entries.append(entry)
    
    return entries


def ingest_goes_hotspots(aws_access_key=None, aws_secret_key=None, satellite="GOES16", hours_back=6):
    """
    Ingest GOES ABI Fire/Hot-Spot data into unified schema
    
    Args:
        aws_access_key: AWS access key
        aws_secret_key: AWS secret key
        satellite: GOES satellite to use (GOES16 or GOES17)
        hours_back: Number of hours to look back
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting {satellite} hotspots, {hours_back}h lookback")
    
    client = GOESHotspotClient(aws_access_key=aws_access_key, aws_secret_key=aws_secret_key)
    hotspots = client.get_latest_hotspots(satellite=satellite, hours_back=hours_back)
    
    entries = []
    for spot in hotspots:
        entry = {
            "source": "goes_hotspot",
            "timestamp": spot.get("detection_time", datetime.now().isoformat()),
            "lat": float(spot["latitude"]) if "latitude" in spot else 0,
            "lon": float(spot["longitude"]) if "longitude" in spot else 0,
            "data": {
                "satellite": spot.get("satellite", satellite),
                "temperature_k": spot.get("temp_k", 0),
                "area_km2": spot.get("area_km2", 0),
                "mask_flag": spot.get("mask_flag", 0),
                "algorithm": spot.get("algorithm", "GOES-ABI-Fire"),
                "confidence": spot.get("confidence", 0.7)
            }
        }
        entries.append(entry)
    
    return entries


def ingest_nifc_fire_perimeters(api_key=None, state=None, days_back=7):
    """
    Ingest NIFC fire perimeters data into unified schema
    
    Args:
        api_key: API key (not required for public data)
        state: State filter (e.g., 'CA', 'OR')
        days_back: Number of days to look back
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting NIFC fire perimeters: state={state}, {days_back}d lookback")
    
    client = NIFCPerimetersClient(api_key=api_key)
    perimeters = client.get_current_perimeters(state=state, days_back=days_back)
    
    entries = []
    for perim in perimeters:
        attrs = perim.get("attributes", {})
        discovery_time = datetime.fromtimestamp(attrs.get("FireDiscoveryDateTime", 0) / 1000).isoformat() if "FireDiscoveryDateTime" in attrs else datetime.now().isoformat()
        
        entry = {
            "source": "nifc_perimeter",
            "timestamp": discovery_time,
            "lat": perim["geometry"]["rings"][0][0][1] if "geometry" in perim and "rings" in perim["geometry"] else 0,
            "lon": perim["geometry"]["rings"][0][0][0] if "geometry" in perim and "rings" in perim["geometry"] else 0,
            "data": {
                "fire_name": attrs.get("FireName", "Unknown"),
                "fire_year": attrs.get("FireYear", datetime.now().year),
                "acres": attrs.get("CalculatedAcres", 0),
                "state": attrs.get("POOState", ""),
                "county": attrs.get("POOCounty", ""),
                "cause": attrs.get("FireCause", "Unknown"),
                "status": attrs.get("FireStatus", "Unknown"),
                "perimeter": perim.get("geometry", {})
            }
        }
        entries.append(entry)
    
    return entries


def ingest_irwin_incidents(api_key=None, state=None):
    """
    Ingest IRWIN incident data into unified schema
    
    Args:
        api_key: API key (not required for public data)
        state: State filter (e.g., 'CA', 'OR')
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting IRWIN incidents: state={state}")
    
    client = IRWINIncidentsClient(api_key=api_key)
    incidents = client.get_active_incidents(state=state)
    
    entries = []
    for inc in incidents:
        attrs = inc.get("attributes", {})
        discovery_time = datetime.fromtimestamp(attrs.get("FireDiscoveryDateTime", 0) / 1000).isoformat() if "FireDiscoveryDateTime" in attrs else datetime.now().isoformat()
        
        entry = {
            "source": "irwin_incident",
            "timestamp": discovery_time,
            "lat": inc["geometry"]["y"] if "geometry" in inc and "y" in inc["geometry"] else 0,
            "lon": inc["geometry"]["x"] if "geometry" in inc and "x" in inc["geometry"] else 0,
            "data": {
                "incident_id": attrs.get("IrwinID", ""),
                "incident_name": attrs.get("IncidentName", "Unknown"),
                "acres": attrs.get("DailyAcres", 0),
                "percent_contained": attrs.get("PercentContained", 0),
                "state": attrs.get("POOState", ""),
                "cause": attrs.get("FireCause", "Unknown"),
                "status": attrs.get("IncidentStatusCode", "Unknown"),
                "personnel": attrs.get("TotalIncidentPersonnel", 0),
                "engines": attrs.get("TotalIncidentEngines", 0),
                "helicopters": attrs.get("TotalIncidentHelicopters", 0),
                "crews": attrs.get("TotalIncidentCrews", 0)
            }
        }
        entries.append(entry)
    
    return entries


def ingest_hrrr_forecast(aws_access_key=None, aws_secret_key=None, lat=0, lon=0, forecast_hours=24):
    """
    Ingest NOAA HRRR forecast data into unified schema
    
    Args:
        aws_access_key: AWS access key
        aws_secret_key: AWS secret key
        lat: Latitude
        lon: Longitude
        forecast_hours: Number of forecast hours
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting HRRR forecast: {lat},{lon}, {forecast_hours}h")
    
    client = NOAAWeatherClient(aws_access_key=aws_access_key, aws_secret_key=aws_secret_key)
    forecast = client.get_hrrr_forecast(lat=lat, lon=lon, forecast_hours=forecast_hours)
    
    entries = []
    for fcs in forecast:
        entry = {
            "source": "hrrr_forecast",
            "timestamp": fcs.get("forecast_time", datetime.now().isoformat()),
            "lat": lat,
            "lon": lon,
            "data": {
                "temperature_c": fcs.get("temperature_c", 0),
                "humidity_percent": fcs.get("humidity_percent", 0),
                "wind_speed_kmh": fcs.get("wind_speed_kmh", 0),
                "wind_direction_deg": fcs.get("wind_direction_deg", 0),
                "precipitation_mm": fcs.get("precipitation_mm", 0),
                "pressure_hpa": fcs.get("pressure_hpa", 1013.25),
                "cloud_cover_percent": fcs.get("cloud_cover_percent", 0)
            }
        }
        entries.append(entry)
    
    return entries


def ingest_hms_smoke(api_key=None, lat=0, lon=0, radius_km=200):
    """
    Ingest NOAA HMS smoke data into unified schema
    
    Args:
        api_key: API key (if needed)
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers
        
    Returns:
        List of unified data entries
    """
    logger.info(f"Ingesting HMS smoke data: {lat},{lon}, r={radius_km}km")
    
    client = NOAAWeatherClient(api_key=api_key)
    smoke_plumes = client.get_smoke_forecast(lat=lat, lon=lon, radius_km=radius_km)
    
    entries = []
    for plume in smoke_plumes:
        entry = {
            "source": "hms_smoke",
            "timestamp": plume.get("start_time", datetime.now().isoformat()),
            "lat": plume.get("latitude", 0),
            "lon": plume.get("longitude", 0),
            "data": {
                "plume_id": plume.get("plume_id", ""),
                "end_time": plume.get("end_time", ""),
                "area_km2": plume.get("area_km2", 0),
                "intensity": plume.get("intensity", "Medium"),
                "source_fire_id": plume.get("source_fire_id", ""),
                "smoke_height_m": plume.get("smoke_height_m", 1000),
                "confidence": plume.get("confidence", "Medium")
            }
        }
        entries.append(entry)
    
    return entries


# Main ingestion function for satellite data sources
def ingest_satellite_sources(config):
    """
    Orchestrate ingestion from all configured satellite data sources
    
    Args:
        config: Dictionary of configuration parameters
        
    Returns:
        List of unified data entries
    """
    all_entries = []
    
    # NASA FIRMS hotspots
    if config.get("enable_nasa_firms", False):
        entries = ingest_nasa_firms_hotspots(
            api_key=config.get("nasa_firms_api_key"),
            lat=config.get("region_center_lat", 0),
            lon=config.get("region_center_lon", 0),
            radius_km=config.get("region_radius_km", 100),
            days=config.get("nasa_firms_days", 1)
        )
        all_entries.extend(entries)
    
    # GOES hotspots
    if config.get("enable_goes_hotspots", False):
        entries = ingest_goes_hotspots(
            aws_access_key=config.get("aws_access_key"),
            aws_secret_key=config.get("aws_secret_key"),
            satellite=config.get("goes_satellite", "GOES16"),
            hours_back=config.get("goes_hours_back", 6)
        )
        all_entries.extend(entries)
    
    # NIFC fire perimeters
    if config.get("enable_nifc_perimeters", False):
        entries = ingest_nifc_fire_perimeters(
            api_key=config.get("nifc_api_key"),
            state=config.get("state_filter"),
            days_back=config.get("nifc_days_back", 7)
        )
        all_entries.extend(entries)
    
    # IRWIN incidents
    if config.get("enable_irwin_incidents", False):
        entries = ingest_irwin_incidents(
            api_key=config.get("irwin_api_key"),
            state=config.get("state_filter")
        )
        all_entries.extend(entries)
    
    # HRRR weather forecast
    if config.get("enable_hrrr_forecast", False):
        entries = ingest_hrrr_forecast(
            aws_access_key=config.get("aws_access_key"),
            aws_secret_key=config.get("aws_secret_key"),
            lat=config.get("region_center_lat", 0),
            lon=config.get("region_center_lon", 0),
            forecast_hours=config.get("forecast_hours", 24)
        )
        all_entries.extend(entries)
    
    # HMS smoke data
    if config.get("enable_hms_smoke", False):
        entries = ingest_hms_smoke(
            api_key=config.get("noaa_api_key"),
            lat=config.get("region_center_lat", 0),
            lon=config.get("region_center_lon", 0),
            radius_km=config.get("region_radius_km", 200)
        )
        all_entries.extend(entries)
    
    return all_entries
