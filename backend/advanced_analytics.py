"""
Advanced analytics engine with AI-based detection and prediction models
for wildfire monitoring and early detection.
"""

import logging
import numpy as np
from datetime import datetime, timedelta
import os
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("firesight.analytics")

# Constants
HIGH_TEMP_THRESHOLD = 45  # °C
MEDIUM_TEMP_THRESHOLD = 35  # °C
HIGH_THERMAL_THRESHOLD = 50  # Thermal index
HIGH_CO2_THRESHOLD = 1000  # ppm

class DetectionModel:
    """Base class for detection models"""
    def __init__(self, model_name="base", confidence_threshold=0.7):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
    
    def load(self, model_path=None):
        """Load the model from file"""
        logger.info(f"Loading {self.model_name} model")
        return True
    
    def predict(self, data):
        """Make predictions using the model"""
        raise NotImplementedError("Subclasses must implement predict()")


class SmokeFireDetectionModel(DetectionModel):
    """Computer vision model for smoke and fire detection from camera images"""
    def __init__(self, model_path=None, confidence_threshold=0.7):
        super().__init__("smoke_fire_cv", confidence_threshold)
        self.classes = ['background', 'smoke', 'fire']
        self.load(model_path)
    
    def load(self, model_path=None):
        """Load PyTorch or TensorFlow model"""
        try:
            # In production, load actual AI model:
            # model_path = model_path or os.path.join(os.path.dirname(__file__), '../models/smoke_fire_detector.pt')
            # import torch
            # self.model = torch.load(model_path)
            # self.model.eval()
            
            # For demo purposes:
            logger.info("Loaded mock smoke/fire detection model")
            return True
        except Exception as e:
            logger.error(f"Failed to load smoke/fire detection model: {e}")
            return False
    
    def predict(self, image_path):
        """Detect smoke and fire in image"""
        try:
            # In production, use actual model inference:
            # import torch
            # import cv2
            # image = cv2.imread(image_path)
            # tensor = self._preprocess_image(image)
            # with torch.no_grad():
            #     outputs = self.model(tensor)
            # return self._process_outputs(outputs)
            
            # For demo purposes, simulate detection results:
            # Generate some sample detections based on the image filename
            if "fire" in image_path.lower() or "smoke" in image_path.lower():
                confidence = 0.85  # Higher confidence for images with fire/smoke in name
            else:
                confidence = 0.3   # Lower confidence otherwise
                
            # Add some randomization to make it more realistic
            import random
            confidence += random.uniform(-0.1, 0.1)
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
            
            has_detection = confidence > self.confidence_threshold
            
            if has_detection:
                class_id = 2 if "fire" in image_path.lower() else 1  # 1=smoke, 2=fire
                return {
                    "detection": True,
                    "class": self.classes[class_id],
                    "confidence": confidence,
                    "bbox": [120, 80, 250, 200]  # x1, y1, x2, y2
                }
            else:
                return {
                    "detection": False,
                    "confidence": confidence
                }
                
        except Exception as e:
            logger.error(f"Error in smoke/fire detection: {e}")
            return {"detection": False, "error": str(e)}


class ThermalAnomalyModel(DetectionModel):
    """Model for detecting thermal anomalies in satellite imagery"""
    def __init__(self, model_path=None, confidence_threshold=0.6):
        super().__init__("thermal_anomaly", confidence_threshold)
        self.load(model_path)
    
    def load(self, model_path=None):
        """Load anomaly detection model"""
        logger.info("Loaded mock thermal anomaly detection model")
        return True
    
    def predict(self, thermal_data):
        """Detect anomalies in thermal data"""
        try:
            # For demo purposes, use rule-based detection
            anomalies = []
            for point in thermal_data:
                if point.get("thermal", 0) > HIGH_THERMAL_THRESHOLD:
                    # Calculate severity based on thermal value
                    severity = min(1.0, point.get("thermal", 0) / 100)
                    anomalies.append({
                        "lat": point.get("lat", 0),
                        "lon": point.get("lon", 0),
                        "thermal_value": point.get("thermal", 0),
                        "severity": severity,
                        "confidence": 0.85
                    })
            
            return {
                "detection": len(anomalies) > 0,
                "anomalies": anomalies,
                "count": len(anomalies)
            }
        except Exception as e:
            logger.error(f"Error in thermal anomaly detection: {e}")
            return {"detection": False, "error": str(e)}


class FirePredictionModel:
    """Predictive model for fire spread and behavior"""
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.loaded = self._load_model()
    
    def _load_model(self):
        """Load the fire prediction model"""
        try:
            # In production, load actual model
            logger.info("Loaded mock fire prediction model")
            return True
        except Exception as e:
            logger.error(f"Failed to load fire prediction model: {e}")
            return False
    
    def predict_spread(self, ignition_point, weather_data, terrain_data=None):
        """Predict fire spread from ignition point given weather and terrain"""
        try:
            # In production, use actual model
            # For demo, implement simplified physics-based spread model
            
            # Extract parameters
            lat = ignition_point.get("lat", 0)
            lon = ignition_point.get("lon", 0)
            
            # Get weather factors
            wind_speed = weather_data.get("wind_speed", 5)  # mph
            wind_direction = weather_data.get("wind_direction", "N")
            temperature = weather_data.get("temperature", 25)  # C
            humidity = weather_data.get("humidity", 30)  # %
            
            # Convert wind direction to degrees
            wind_dir_map = {"N": 0, "NE": 45, "E": 90, "SE": 135, 
                           "S": 180, "SW": 225, "W": 270, "NW": 315}
            wind_dir_degrees = wind_dir_map.get(wind_direction, 0)
            
            # Calculate base spread rate based on weather
            # Higher temp, lower humidity, higher wind = faster spread
            base_spread_rate = (
                (temperature / 40) * 0.4 + 
                ((100 - humidity) / 100) * 0.3 + 
                (wind_speed / 30) * 0.3
            )
            
            # Clamp spread rate between 0.1 and 2.0 km/h
            spread_rate = max(0.1, min(2.0, base_spread_rate))
            
            # Generate 1-hour, 3-hour, and 6-hour spread predictions
            predictions = []
            
            for hours in [1, 3, 6]:
                # For each timeframe, calculate spread distance and direction
                spread_km = spread_rate * hours
                
                # Calculate spread in all directions (simplified elliptical model)
                # Wind direction affects the spread shape
                perimeters = []
                
                # Sample 36 points around the perimeter (every 10 degrees)
                for angle_deg in range(0, 360, 10):
                    # Adjust spread based on angle relative to wind direction
                    # Maximum spread is in the wind direction
                    angle_diff = abs((angle_deg - wind_dir_degrees + 360) % 360)
                    angle_factor = 1.0
                    
                    if angle_diff <= 90:  # Downwind - maximum spread
                        angle_factor = 1.0
                    elif angle_diff >= 270:  # Upwind - minimum spread
                        angle_factor = 0.2
                    else:  # Crosswind - moderate spread
                        angle_factor = 0.6
                    
                    # Calculate distance for this angle
                    distance = spread_km * angle_factor
                    
                    # Convert to lat/lon offset (approximate)
                    angle_rad = angle_deg * (3.14159 / 180.0)
                    lat_offset = distance * 0.009 * np.cos(angle_rad)
                    lon_offset = distance * 0.009 * np.sin(angle_rad) / np.cos(lat * 0.0174533)
                    
                    perimeters.append({
                        "lat": lat + lat_offset,
                        "lon": lon + lon_offset
                    })
                
                # Append the prediction for this timeframe
                predictions.append({
                    "hours": hours,
                    "timestamp": (datetime.now() + timedelta(hours=hours)).isoformat(),
                    "perimeter": perimeters,
                    "spread_km": spread_km,
                    "confidence": max(0.3, 1.0 - (hours / 10))  # Confidence decreases with time
                })
            
            return {
                "ignition_point": {"lat": lat, "lon": lon},
                "predictions": predictions,
                "factors": {
                    "temperature": temperature,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "wind_direction": wind_direction
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fire spread prediction: {e}")
            return {"error": str(e)}


class ResourceOptimizer:
    """Reinforcement learning model for optimizing firefighting resource deployment"""
    def __init__(self):
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load RL model for resource optimization"""
        try:
            # In production, load trained RL model
            self.model_loaded = True
            logger.info("Loaded mock resource optimization model")
            return True
        except Exception as e:
            logger.error(f"Failed to load resource optimization model: {e}")
            return False
    
    def optimize_resources(self, fire_predictions, available_resources):
        """Optimize resource allocation based on fire predictions"""
        try:
            if not self.model_loaded:
                raise ValueError("Model not loaded")
            
            # Get fire parameters
            ignition_point = fire_predictions.get("ignition_point", {})
            predictions = fire_predictions.get("predictions", [])
            
            if not predictions:
                return {"error": "No fire predictions provided"}
            
            # Get the 1-hour prediction as immediate concern
            one_hour = next((p for p in predictions if p.get("hours") == 1), None)
            
            # Get list of available resources
            firefighters = available_resources.get("firefighters", 0)
            engines = available_resources.get("engines", 0)
            aircraft = available_resources.get("aircraft", 0)
            water_tankers = available_resources.get("water_tankers", 0)
            
            # In production, use RL model to optimize
            # For demo, use rule-based allocation
            
            # Calculate total perimeter length (approximate)
            perimeter_points = one_hour.get("perimeter", []) if one_hour else []
            perimeter_length_km = one_hour.get("spread_km", 1) * 2 * 3.14159 if one_hour else 1
            
            # Basic allocation rules:
            # - Each fire engine can cover ~0.5 km of perimeter
            # - Each firefighter team (5 people) can cover ~0.2 km
            # - Each aircraft can support ~1 km of perimeter
            
            required_engines = max(1, int(perimeter_length_km / 0.5))
            required_firefighter_teams = max(1, int(perimeter_length_km / 0.2))
            required_aircraft = max(1, int(perimeter_length_km / 1.0))
            required_water = perimeter_length_km * 10000  # Liters
            
            # Adjust for available resources
            allocated_engines = min(required_engines, engines)
            allocated_firefighter_teams = min(required_firefighter_teams, int(firefighters / 5))
            allocated_aircraft = min(required_aircraft, aircraft)
            
            # Calculate expected containment effectiveness
            engine_effectiveness = allocated_engines / required_engines if required_engines > 0 else 1
            firefighter_effectiveness = allocated_firefighter_teams / required_firefighter_teams if required_firefighter_teams > 0 else 1
            aircraft_effectiveness = allocated_aircraft / required_aircraft if required_aircraft > 0 else 1
            
            # Overall effectiveness (weighted average)
            overall_effectiveness = (
                engine_effectiveness * 0.4 +
                firefighter_effectiveness * 0.4 +
                aircraft_effectiveness * 0.2
            )
            
            # Strategic locations based on wind direction and terrain
            # In production, would use detailed terrain analysis
            wind_direction = fire_predictions.get("factors", {}).get("wind_direction", "N")
            
            # Generate deployment locations
            deployment_locations = []
            
            # Basic strategy: Position resources around perimeter with focus downwind
            for i in range(min(len(perimeter_points), allocated_engines + allocated_firefighter_teams)):
                point = perimeter_points[i % len(perimeter_points)]
                deployment_locations.append({
                    "lat": point.get("lat"),
                    "lon": point.get("lon"),
                    "resources": {
                        "engines": 1 if i < allocated_engines else 0,
                        "firefighters": 5 if i < allocated_firefighter_teams else 0,
                        "type": "ground"
                    }
                })
            
            # Position aircraft for aerial support
            if allocated_aircraft > 0:
                deployment_locations.append({
                    "lat": ignition_point.get("lat", 0),
                    "lon": ignition_point.get("lon", 0),
                    "resources": {
                        "aircraft": allocated_aircraft,
                        "type": "aerial"
                    }
                })
            
            return {
                "allocation": {
                    "engines": allocated_engines,
                    "firefighters": allocated_firefighter_teams * 5,
                    "aircraft": allocated_aircraft,
                    "water_required_liters": required_water
                },
                "effectiveness": overall_effectiveness,
                "deployment_locations": deployment_locations,
                "estimated_containment_time_hours": max(1, int(6 / overall_effectiveness)) if overall_effectiveness > 0 else 24
            }
            
        except Exception as e:
            logger.error(f"Error in resource optimization: {e}")
            return {"error": str(e)}


# Original rule-based threat detection
def _parse_ts(ts):
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


def detect_threats(fused_entries):
    """Very simple rule-based detection using satellite and sensor data."""
    sensors = [e for e in fused_entries if e["source"] == "sensor"]
    satellites = [e for e in fused_entries if e["source"] == "satellite"]

    alerts = []
    for sat in satellites:
        if sat["data"].get("thermal", 0) < 50:
            continue
        sat_time = _parse_ts(sat["timestamp"])
        for sensor in sensors:
            sensor_time = _parse_ts(sensor["timestamp"])
            if abs((sensor_time - sat_time).total_seconds()) <= 300:  # 5 min
                if sensor["data"].get("temperature", 0) >= 35:
                    severity = "high" if sensor["data"]["temperature"] >= 50 else "medium"
                    predicted_spread = (sat["data"]["thermal"] / 50) * 1.0
                    alerts.append({
                        "type": "detection",
                        "severity": severity,
                        "timestamp": sat["timestamp"],
                        "lat": sat["lat"],
                        "lon": sat["lon"],
                        "details": {
                            "thermal": sat["data"]["thermal"],
                            "temperature": sensor["data"]["temperature"],
                            "humidity": sensor["data"]["humidity"],
                            "predicted_spread_km2": predicted_spread
                        }
                    })
    return alerts


# Enhanced analytics functions using AI models
def detect_wildfires_comprehensive(fused_entries, config=None):
    """
    Advanced wildfire detection using multi-modal data fusion and AI models.
    Combines camera imagery, thermal data, IoT sensors, and weather data.
    """
    if config is None:
        config = {}
    
    # Initialize detection models
    smoke_fire_detector = SmokeFireDetectionModel(
        confidence_threshold=config.get("smoke_fire_confidence_threshold", 0.7)
    )
    thermal_detector = ThermalAnomalyModel(
        confidence_threshold=config.get("thermal_confidence_threshold", 0.6)
    )
    
    # Group data by source type
    cameras = [e for e in fused_entries if e["source"] in ("camera", "rtsp_camera")]
    satellites = [e for e in fused_entries if e["source"] in ("satellite", "nasa_firms")]
    sensors = [e for e in fused_entries if e["source"] in ("sensor", "iot_sensor")]
    weather = [e for e in fused_entries if e["source"] == "weather_api"]
    
    # Detection results
    detections = []
    
    # 1. Process camera data with CV model
    for camera in cameras:
        if "file" in camera["data"]:
            # Construct full path to image file
            file_path = os.path.join("data", camera["data"]["file"])
            
            # Detect smoke/fire in image
            result = smoke_fire_detector.predict(file_path)
            
            if result.get("detection", False):
                detections.append({
                    "type": "visual_detection",
                    "source": "camera",
                    "confidence": result.get("confidence", 0),
                    "class": result.get("class", "unknown"),
                    "timestamp": camera["timestamp"],
                    "lat": camera["lat"],
                    "lon": camera["lon"],
                    "details": {
                        "detection_box": result.get("bbox"),
                        "image_file": camera["data"]["file"]
                    }
                })
    
    # 2. Process satellite thermal data
    satellite_data = [{
        "lat": sat["lat"],
        "lon": sat["lon"],
        "thermal": sat["data"].get("thermal", 0) 
    } for sat in satellites]
    
    thermal_results = thermal_detector.predict(satellite_data)
    
    if thermal_results.get("detection", False) and "anomalies" in thermal_results:
        for anomaly in thermal_results["anomalies"]:
            # Find matching satellite entry
            sat_entry = next((s for s in satellites if 
                             abs(s["lat"] - anomaly["lat"]) < 0.01 and 
                             abs(s["lon"] - anomaly["lon"]) < 0.01), None)
            
            if sat_entry:
                detections.append({
                    "type": "thermal_anomaly",
                    "source": "satellite",
                    "confidence": anomaly.get("confidence", 0),
                    "severity": "high" if anomaly.get("thermal_value", 0) > HIGH_THERMAL_THRESHOLD else "medium",
                    "timestamp": sat_entry["timestamp"],
                    "lat": anomaly["lat"],
                    "lon": anomaly["lon"],
                    "details": {
                        "thermal_value": anomaly["thermal_value"]
                    }
                })
    
    # 3. Process sensor data
    for sensor in sensors:
        # Check for high temperature, low humidity, high CO2, or smoke detection
        temp = sensor["data"].get("temperature", 0)
        humidity = sensor["data"].get("humidity", 50)
        co2 = sensor["data"].get("co2", 0)
        smoke_detected = sensor["data"].get("smoke_detected", False)
        
        if (temp >= MEDIUM_TEMP_THRESHOLD or
            humidity < 20 or
            co2 > HIGH_CO2_THRESHOLD or
            smoke_detected):
            
            # Determine severity
            if temp >= HIGH_TEMP_THRESHOLD or co2 > HIGH_CO2_THRESHOLD or smoke_detected:
                severity = "high"
                confidence = 0.85
            else:
                severity = "medium"
                confidence = 0.7
            
            detections.append({
                "type": "sensor_alert",
                "source": "sensor",
                "confidence": confidence,
                "severity": severity,
                "timestamp": sensor["timestamp"],
                "lat": sensor["lat"],
                "lon": sensor["lon"],
                "details": {
                    "temperature": temp,
                    "humidity": humidity,
                    "co2": co2,
                    "smoke_detected": smoke_detected
                }
            })
    
    # 4. Correlate detections by location and time
    # Group detections by location (grid cells of ~1km)
    grid_size = 0.01  # degrees, approx 1km
    detection_grids = {}
    
    for detection in detections:
        # Create grid key based on rounded coordinates
        grid_key = (
            round(detection["lat"] / grid_size) * grid_size,
            round(detection["lon"] / grid_size) * grid_size
        )
        
        if grid_key not in detection_grids:
            detection_grids[grid_key] = []
        
        detection_grids[grid_key].append(detection)
    
    # 5. Generate final correlated alerts
    alerts = []
    
    for grid_key, grid_detections in detection_grids.items():
        # If we have multiple detection types in the same area, it's higher confidence
        detection_types = set(d["type"] for d in grid_detections)
        detection_sources = set(d["source"] for d in grid_detections)
        
        # Determine highest severity and confidence
        severity_levels = ["low", "medium", "high"]
        severity_idx = 0
        max_confidence = 0
        
        for detection in grid_detections:
            current_severity = detection.get("severity", "low")
            current_idx = severity_levels.index(current_severity) if current_severity in severity_levels else 0
            severity_idx = max(severity_idx, current_idx)
            
            max_confidence = max(max_confidence, detection.get("confidence", 0))
        
        # Boost confidence if we have multiple detection types
        if len(detection_types) > 1:
            confidence_boost = min(0.15, 0.05 * len(detection_types))
            max_confidence = min(0.95, max_confidence + confidence_boost)
        
        # Sort detections by timestamp
        grid_detections.sort(key=lambda d: d.get("timestamp", ""))
        latest_timestamp = grid_detections[-1].get("timestamp") if grid_detections else datetime.now().isoformat()
        
        # Create alert
        alert = {
            "type": "wildfire_detection",
            "severity": severity_levels[severity_idx],
            "confidence": max_confidence,
            "timestamp": latest_timestamp,
            "lat": grid_key[0],
            "lon": grid_key[1],
            "details": {
                "detection_types": list(detection_types),
                "detection_sources": list(detection_sources),
                "detection_count": len(grid_detections)
            }
        }
        
        # Add detailed detections
        alert["details"]["detections"] = grid_detections
        
        # If we have weather data, include fire weather index
        if weather:
            latest_weather = max(weather, key=lambda w: w.get("timestamp", ""))
            alert["details"]["weather"] = {
                "temperature": latest_weather["data"].get("temperature", 0),
                "humidity": latest_weather["data"].get("humidity", 0),
                "wind_speed": latest_weather["data"].get("wind_speed", "0"),
                "wind_direction": latest_weather["data"].get("wind_direction", "N")
            }
        
        alerts.append(alert)
    
    return alerts


def predict_fire_spread(fire_alerts, fused_entries, config=None):
    """
    Generate fire spread predictions for detected fires.
    """
    if config is None:
        config = {}
    
    # Initialize fire prediction model
    fire_model = FirePredictionModel()
    
    # Get weather data from fused entries
    weather_entries = [e for e in fused_entries if e["source"] == "weather_api"]
    latest_weather = weather_entries[-1]["data"] if weather_entries else {}
    
    if not latest_weather:
        # Default weather data if none available
        latest_weather = {
            "temperature": 30,
            "humidity": 30,
            "wind_speed": 10,
            "wind_direction": "N"
        }
    
    # For each high-severity fire alert, predict spread
    predictions = []
    
    for alert in fire_alerts:
        # Only predict for high severity alerts with high confidence
        if alert.get("severity") == "high" and alert.get("confidence", 0) >= 0.7:
            ignition_point = {
                "lat": alert["lat"],
                "lon": alert["lon"]
            }
            
            # Get prediction
            prediction = fire_model.predict_spread(ignition_point, latest_weather)
            
            if "error" not in prediction:
                predictions.append({
                    "alert_id": alert.get("id", str(hash(alert["timestamp"] + str(alert["lat"]) + str(alert["lon"])))),
                    "detection": alert,
                    "prediction": prediction
                })
    
    return predictions


def optimize_firefighting_resources(fire_predictions, available_resources=None):
    """
    Optimize allocation of firefighting resources based on fire predictions.
    """
    if available_resources is None:
        # Default resources if none specified
        available_resources = {
            "firefighters": 100,
            "engines": 10,
            "aircraft": 2,
            "water_tankers": 5
        }
    
    optimizer = ResourceOptimizer()
    
    # For each fire prediction, optimize resources
    allocations = []
    
    for pred in fire_predictions:
        result = optimizer.optimize_resources(pred["prediction"], available_resources)
        
        if "error" not in result:
            allocations.append({
                "fire_id": pred.get("alert_id"),
                "location": {
                    "lat": pred["detection"]["lat"],
                    "lon": pred["detection"]["lon"]
                },
                "allocation": result
            })
            
            # Update available resources for next allocation
            available_resources["firefighters"] -= result["allocation"]["firefighters"]
            available_resources["engines"] -= result["allocation"]["engines"]
            available_resources["aircraft"] -= result["allocation"]["aircraft"]
            
            # Ensure no negative values
            for key in available_resources:
                available_resources[key] = max(0, available_resources[key])
    
    return {
        "allocations": allocations,
        "remaining_resources": available_resources
    }


def generate_ics_incident_report(fire_alerts, fire_predictions):
    """
    Generate data for ICS 209 incident reports based on fire detections and predictions.
    """
    reports = []
    
    for i, alert in enumerate(fire_alerts):
        # Find matching prediction if available
        prediction = next((p for p in fire_predictions if p.get("detection", {}).get("lat") == alert["lat"] and 
                          p.get("detection", {}).get("lon") == alert["lon"]), None)
        
        # Get the 6-hour prediction if available
        spread_6hr = next((p for p in prediction["prediction"]["predictions"] 
                          if p.get("hours") == 6), {}) if prediction else {}
        
        # Calculate area
        area_acres = 0
        if spread_6hr and "spread_km" in spread_6hr:
            # Convert km radius to acres (circular approximation)
            radius_km = spread_6hr["spread_km"]
            area_km2 = 3.14159 * (radius_km ** 2)
            area_acres = area_km2 * 247.105  # 1 km² = 247.105 acres
        
        # Format timestamp for report
        timestamp = datetime.fromisoformat(alert["timestamp"].replace('Z', '+00:00')) if "timestamp" in alert else datetime.now()
        report_date = timestamp.strftime("%Y-%m-%d")
        report_time = timestamp.strftime("%H:%M")
        
        # Generate ICS 209 compatible report data
        report = {
            "incident_name": f"Wildfire #{i+1}",
            "incident_number": f"FS-{timestamp.strftime('%Y%m%d')}-{i+1}",
            "report_version": 1,
            "report_date": report_date,
            "report_time": report_time,
            "incident_type": "Wildfire",
            "incident_location": {
                "lat": alert["lat"],
                "lon": alert["lon"],
                "description": f"Lat: {alert['lat']:.6f}, Lon: {alert['lon']:.6f}"
            },
            "incident_size": {
                "acres": int(area_acres),
                "percent_contained": 0
            },
            "significant_events": [
                f"FireSight AI detected wildfire at {report_time} with {alert.get('confidence', 0)*100:.0f}% confidence"
            ],
            "threat_summary": {
                "structures_threatened": estimate_structures_threatened(alert["lat"], alert["lon"], spread_6hr.get("spread_km", 1)),
                "evacuations_in_place": alert.get("severity") == "high",
                "critical_infrastructure": estimate_critical_infrastructure(alert["lat"], alert["lon"], spread_6hr.get("spread_km", 1))
            },
            "weather": alert.get("details", {}).get("weather", {
                "temperature": 0,
                "humidity": 0,
                "wind_speed": "Unknown",
                "wind_direction": "Unknown"
            }),
            "resources_assigned": {
                "engines": 0,
                "helicopters": 0,
                "dozers": 0,
                "crews": 0,
                "personnel_count": 0
            },
            "prepared_by": "FireSight AI System"
        }
        
        reports.append(report)
    
    return reports


# Utility functions for incident reporting
def estimate_structures_threatened(lat, lon, radius_km):
    """Estimate number of structures threatened based on location and radius."""
    # In production, would use GIS data to count structures in the area
    # For demo, use simple population density approximation
    
    # Simplified population density based on coordinates (just for demo)
    # Higher population in urban areas, lower in rural
    is_urban = abs(lat) < 50 and (lon > -125 and lon < -65 or lon > 100 and lon < 150)
    
    if is_urban:
        # Urban area - higher density
        structures_per_km2 = 150
    else:
        # Rural area - lower density
        structures_per_km2 = 10
    
    # Calculate area in km²
    area_km2 = 3.14159 * (radius_km ** 2)
    
    # Estimate structures
    structures = int(area_km2 * structures_per_km2)
    
    return structures


def estimate_critical_infrastructure(lat, lon, radius_km):
    """Estimate critical infrastructure in the affected area."""
    # In production, would use actual infrastructure GIS data
    # For demo, use simple approximation
    
    # Simple check for potential infrastructure based on coordinates
    infrastructure = []
    
    # Power lines approximation
    if abs((abs(lat) % 0.5) - 0.25) < 0.05:
        infrastructure.append({
            "type": "Power Lines",
            "name": "High Voltage Transmission",
            "status": "Threatened"
        })
    
    # Water reservoirs approximation
    if abs((abs(lon) % 1.0) - 0.5) < 0.1:
        infrastructure.append({
            "type": "Water Resource",
            "name": "Reservoir",
            "status": "Potentially Threatened"
        })
    
    # Highways approximation
    if abs((abs(lat + lon) % 1.0) - 0.5) < 0.1:
        infrastructure.append({
            "type": "Transportation",
            "name": "Highway",
            "status": "Monitor"
        })
    
    # Always include cell towers if radius is large enough
    if radius_km > 1.0:
        infrastructure.append({
            "type": "Communications",
            "name": "Cell Tower",
            "status": "Threatened"
        })
    
    return infrastructure
