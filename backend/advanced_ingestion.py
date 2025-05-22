"""
Extended Data Ingestion Module with support for RTSP/HTTP camera streams,
satellite APIs, IoT sensor networks, and weather/grid data.
"""

import os
import csv
import json
import requests
from datetime import datetime
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.ingestion")

# Constants and configuration
UNIFIED_SCHEMA_FIELDS = ["source", "timestamp", "lat", "lon", "data"]
DEFAULT_TIMEOUT = 10  # Default timeout for API requests

class StreamConnection:
    """Base class for managing stream connections"""
    def __init__(self, connection_string, connection_type="generic"):
        self.connection_string = connection_string
        self.connection_type = connection_type
        self.connected = False
        self.last_error = None
    
    def connect(self):
        """Establish connection to the stream"""
        logger.info(f"Connecting to {self.connection_type} stream: {self.connection_string}")
        self.connected = True
        return True
    
    def disconnect(self):
        """Close the stream connection"""
        logger.info(f"Disconnecting from {self.connection_type} stream")
        self.connected = False
    
    def is_connected(self):
        """Check if the stream is connected"""
        return self.connected
    
    def get_last_error(self):
        """Get the last error message"""
        return self.last_error


class RTSPStreamConnection(StreamConnection):
    """Handles RTSP video streams from cameras"""
    def __init__(self, rtsp_url):
        super().__init__(rtsp_url, "RTSP")
        self.frame_count = 0
    
    def connect(self):
        """Connect to RTSP stream - in production would use OpenCV"""
        logger.info(f"Connecting to RTSP stream: {self.connection_string}")
        try:
            # In production: Use OpenCV to connect to the stream
            # import cv2
            # self.cap = cv2.VideoCapture(self.connection_string)
            # return self.cap.isOpened()
            
            # For demo purposes:
            self.connected = True
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to connect to RTSP stream: {e}")
            return False
    
    def get_frame(self):
        """Get the latest frame from the stream"""
        if not self.connected:
            logger.error("Not connected to RTSP stream")
            return None
        
        try:
            # In production: Return actual frame from OpenCV
            # ret, frame = self.cap.read()
            # if ret:
            #    return frame
            # return None
            
            # For demo purposes:
            self.frame_count += 1
            return {"frame_id": self.frame_count, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading from RTSP stream: {e}")
            return None


class MQTTConnection(StreamConnection):
    """Handles MQTT connections for IoT devices"""
    def __init__(self, broker_url, port=1883, username=None, password=None, topics=None):
        super().__init__(broker_url, "MQTT")
        self.port = port
        self.username = username
        self.password = password
        self.topics = topics or ["sensors/#"]
        self.messages = []
    
    def connect(self):
        """Connect to MQTT broker - in production would use paho-mqtt"""
        logger.info(f"Connecting to MQTT broker: {self.connection_string}:{self.port}")
        try:
            # In production: Use paho-mqtt to connect
            # import paho.mqtt.client as mqtt
            # self.client = mqtt.Client()
            # if self.username and self.password:
            #     self.client.username_pw_set(self.username, self.password)
            # self.client.on_message = self._on_message
            # self.client.connect(self.connection_string, self.port)
            # for topic in self.topics:
            #     self.client.subscribe(topic)
            # self.client.loop_start()
            
            # For demo purposes:
            self.connected = True
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def _on_message(self, client, userdata, message):
        """Callback for MQTT messages"""
        try:
            payload = json.loads(message.payload.decode())
            self.messages.append({
                "topic": message.topic,
                "payload": payload,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def get_messages(self, clear=True):
        """Get received messages and optionally clear the queue"""
        messages = self.messages.copy()
        if clear:
            self.messages = []
        return messages


class APIClient:
    """Generic API client for data sources"""
    def __init__(self, base_url, api_key=None, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
    
    def get(self, endpoint, params=None):
        """Make a GET request to the API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None


# Original functions for demo data ingestion
def ingest_camera(directory, lat=0.0, lon=0.0):
    """Ingest dummy camera frames from a directory."""
    entries = []
    for name in sorted(os.listdir(directory)):
        if not name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        timestamp = "2023-01-01T00:04:00Z"  # static timestamp for demo
        entry = {
            "source": "camera",
            "timestamp": timestamp,
            "lat": lat,
            "lon": lon,
            "data": {
                "file": name
            }
        }
        entries.append(entry)
    return entries

def ingest_satellite(csv_file):
    """Ingest satellite thermal data from a CSV file."""
    entries = []
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {
                "source": "satellite",
                "timestamp": row["timestamp"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "data": {
                    "thermal": float(row["thermal"])
                }
            }
            entries.append(entry)
    return entries

def ingest_sensor(json_file):
    """Ingest IoT sensor logs from a JSON file."""
    entries = []
    with open(json_file) as f:
        records = json.load(f)
    for rec in records:
        entry = {
            "source": "sensor",
            "timestamp": rec["timestamp"],
            "lat": rec["location"]["lat"],
            "lon": rec["location"]["lon"],
            "data": {
                "temperature": rec["readings"]["temperature"],
                "humidity": rec["readings"]["humidity"],
                "co2": rec["readings"].get("co2", 0),
                "smoke_detected": rec["readings"].get("smoke_detected", False)
            }
        }
        entries.append(entry)
    return entries


# New extended ingestion functions for production use
def ingest_rtsp_camera_feed(rtsp_url, lat=0.0, lon=0.0, duration_seconds=30):
    """Ingest video feed from RTSP camera stream for specified duration."""
    logger.info(f"Starting RTSP camera ingestion from {rtsp_url}")
    entries = []
    
    try:
        stream = RTSPStreamConnection(rtsp_url)
        if not stream.connect():
            logger.error(f"Failed to connect to RTSP stream: {stream.get_last_error()}")
            return entries
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            frame = stream.get_frame()
            if frame:
                timestamp = datetime.now().isoformat()
                entry = {
                    "source": "rtsp_camera",
                    "timestamp": timestamp,
                    "lat": lat,
                    "lon": lon,
                    "data": {
                        "frame_id": frame.get("frame_id", 0),
                        "stream_url": rtsp_url
                        # In production: process frame for smoke/fire detection here
                        # "detection_results": process_frame_for_detection(frame)
                    }
                }
                entries.append(entry)
            time.sleep(0.5)  # Process at 2fps for demo
            
        stream.disconnect()
    except Exception as e:
        logger.error(f"Error in RTSP camera ingestion: {e}")
    
    return entries

def ingest_nasa_firms_data(api_key=None, days=1, lat=0.0, lon=0.0, radius_km=50):
    """Ingest satellite fire data from NASA FIRMS API."""
    logger.info("Starting NASA FIRMS data ingestion")
    entries = []
    
    try:
        # NASA FIRMS API parameters
        api_client = APIClient(
            "https://firms.modaps.eosdis.nasa.gov/api/area/csv",
            api_key=api_key
        )
        
        # For demo, using sample params (would use real coordinates in production)
        params = {
            "source": "VIIRS_SNPP_NRT",
            "lat": lat,
            "lon": lon,
            "radius": radius_km,
            "days": days
        }
        
        # In production we'd make the actual API call
        # data = api_client.get("", params=params)
        
        # For demo purposes, simulate API response with sample data
        sample_data = [
            {"latitude": lat + 0.1, "longitude": lon + 0.1, "acq_date": "2023-01-01", "acq_time": "13:24", "confidence": "nominal", "frp": 15.2},
            {"latitude": lat + 0.2, "longitude": lon + 0.05, "acq_date": "2023-01-01", "acq_time": "13:30", "confidence": "high", "frp": 25.7}
        ]
        
        for item in sample_data:
            # Format timestamp from date and time
            timestamp = f"{item['acq_date']}T{item['acq_time']}:00Z"
            entry = {
                "source": "nasa_firms",
                "timestamp": timestamp,
                "lat": item["latitude"],
                "lon": item["longitude"],
                "data": {
                    "confidence": item["confidence"],
                    "frp": item["frp"]  # Fire Radiative Power
                }
            }
            entries.append(entry)
    except Exception as e:
        logger.error(f"Error in NASA FIRMS ingestion: {e}")
    
    return entries

def ingest_iot_sensors(mqtt_broker="localhost", port=1883, topic="sensors/#"):
    """Ingest data from IoT sensors via MQTT."""
    logger.info(f"Starting IoT sensor ingestion from MQTT broker {mqtt_broker}")
    entries = []
    
    try:
        # Connect to MQTT broker
        mqtt_client = MQTTConnection(mqtt_broker, port=port, topics=[topic])
        if not mqtt_client.connect():
            logger.error(f"Failed to connect to MQTT broker: {mqtt_client.get_last_error()}")
            return entries
        
        # Wait for some messages to arrive (in real app would use callbacks)
        time.sleep(5)
        
        # Get messages
        messages = mqtt_client.get_messages()
        
        # Process messages
        for msg in messages:
            if "payload" in msg and "location" in msg["payload"]:
                entry = {
                    "source": "iot_sensor",
                    "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                    "lat": msg["payload"]["location"].get("lat", 0),
                    "lon": msg["payload"]["location"].get("lon", 0),
                    "data": msg["payload"].get("readings", {})
                }
                entries.append(entry)
        
        mqtt_client.disconnect()
    except Exception as e:
        logger.error(f"Error in IoT sensor ingestion: {e}")
    
    return entries

def ingest_weather_data(lat=0.0, lon=0.0, api_key=None):
    """Ingest weather data from NOAA or other weather APIs."""
    logger.info(f"Starting weather data ingestion for coordinates: {lat}, {lon}")
    entries = []
    
    try:
        # Setup API client - would use actual NOAA API in production
        api_client = APIClient(
            "https://api.weather.gov",
            api_key=api_key
        )
        
        # For demo purposes, simulate API response
        # In production: data = api_client.get(f"points/{lat},{lon}/forecast")
        
        sample_data = {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "temperature": 32,
                        "temperatureUnit": "C",
                        "windSpeed": "15 mph",
                        "windDirection": "NE",
                        "relativeHumidity": {"value": 15},
                        "probabilityOfPrecipitation": {"value": 0}
                    }
                ]
            }
        }
        
        # Process the data
        if "properties" in sample_data and "periods" in sample_data["properties"]:
            for period in sample_data["properties"]["periods"]:
                entry = {
                    "source": "weather_api",
                    "timestamp": datetime.now().isoformat(),
                    "lat": lat,
                    "lon": lon,
                    "data": {
                        "temperature": period["temperature"],
                        "temperature_unit": period["temperatureUnit"],
                        "wind_speed": period["windSpeed"],
                        "wind_direction": period["windDirection"],
                        "humidity": period["relativeHumidity"]["value"],
                        "precipitation_probability": period["probabilityOfPrecipitation"]["value"]
                    }
                }
                entries.append(entry)
                
    except Exception as e:
        logger.error(f"Error in weather data ingestion: {e}")
    
    return entries

def ingest_utility_grid_data(api_endpoint, api_key=None):
    """Ingest utility grid telemetry data."""
    logger.info(f"Starting utility grid data ingestion from {api_endpoint}")
    entries = []
    
    try:
        # Setup API client - would use actual utility API in production
        api_client = APIClient(
            api_endpoint,
            api_key=api_key
        )
        
        # For demo purposes, simulate API response
        # In production: data = api_client.get("grid-status")
        
        sample_data = [
            {
                "substation_id": "PGE-SUB-1023",
                "location": {"lat": 34.052, "lon": -118.243},
                "transmission_lines": [
                    {"id": "TL-1023-A", "voltage": 138, "load_percent": 75, "status": "active"},
                    {"id": "TL-1023-B", "voltage": 138, "load_percent": 62, "status": "active"}
                ],
                "timestamp": "2023-01-01T12:30:00Z"
            }
        ]
        
        # Process the data
        for substation in sample_data:
            for line in substation["transmission_lines"]:
                entry = {
                    "source": "utility_grid",
                    "timestamp": substation["timestamp"],
                    "lat": substation["location"]["lat"],
                    "lon": substation["location"]["lon"],
                    "data": {
                        "substation_id": substation["substation_id"],
                        "transmission_line_id": line["id"],
                        "voltage": line["voltage"],
                        "load_percent": line["load_percent"],
                        "status": line["status"]
                    }
                }
                entries.append(entry)
                
    except Exception as e:
        logger.error(f"Error in utility grid data ingestion: {e}")
    
    return entries

# Main ingestion orchestration function
def ingest_all_sources(config):
    """Orchestrate ingestion from all configured data sources."""
    all_entries = []
    
    # Camera feeds
    if config.get("enable_camera_feeds", False):
        for camera in config.get("camera_feeds", []):
            entries = ingest_rtsp_camera_feed(
                camera["url"], 
                lat=camera.get("lat", 0), 
                lon=camera.get("lon", 0),
                duration_seconds=config.get("camera_duration_seconds", 30)
            )
            all_entries.extend(entries)
    
    # NASA FIRMS satellite data
    if config.get("enable_nasa_firms", False):
        entries = ingest_nasa_firms_data(
            api_key=config.get("nasa_firms_api_key"),
            days=config.get("nasa_firms_days", 1),
            lat=config.get("region_center_lat", 0),
            lon=config.get("region_center_lon", 0),
            radius_km=config.get("region_radius_km", 50)
        )
        all_entries.extend(entries)
    
    # IoT sensors via MQTT
    if config.get("enable_iot_sensors", False):
        entries = ingest_iot_sensors(
            mqtt_broker=config.get("mqtt_broker", "localhost"),
            port=config.get("mqtt_port", 1883),
            topic=config.get("mqtt_topic", "sensors/#")
        )
        all_entries.extend(entries)
    
    # Weather data
    if config.get("enable_weather_data", False):
        entries = ingest_weather_data(
            lat=config.get("region_center_lat", 0),
            lon=config.get("region_center_lon", 0),
            api_key=config.get("weather_api_key")
        )
        all_entries.extend(entries)
    
    # Utility grid data
    if config.get("enable_utility_grid", False):
        entries = ingest_utility_grid_data(
            api_endpoint=config.get("utility_api_endpoint", ""),
            api_key=config.get("utility_api_key")
        )
        all_entries.extend(entries)
    
    return all_entries
