"""
FireSight AI API Server
FastAPI-based REST API for the FireSight wildfire monitoring platform
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ingestion import ingest_camera, ingest_satellite, ingest_sensor
from fusion import fuse_streams
from analytics import detect_threats
from alert import generate_alerts

app = FastAPI(
    title="FireSight AI API",
    description="REST API for wildfire monitoring and early detection",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class Alert(BaseModel):
    type: str
    severity: str
    timestamp: str
    lat: float
    lon: float
    details: Dict[str, Any]

class DataSummary(BaseModel):
    timestamp: str
    total_sources: int
    camera_count: int
    satellite_count: int
    sensor_count: int
    threat_level: str

class PredictionRequest(BaseModel):
    lat: float
    lon: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None

class PredictionResponse(BaseModel):
    risk_level: str
    confidence: float
    predicted_spread_km: float
    time_to_spread_hours: float

# Global cache for demo data
_cached_alerts = []
_last_update = None

def _get_latest_data():
    """Get latest fused data and alerts"""
    global _cached_alerts, _last_update
    
    # Cache for 30 seconds to simulate real-time updates
    now = datetime.now()
    if _last_update and (now - _last_update).seconds < 30:
        return _cached_alerts
    
    try:
        # Get data directory path
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Ingest data
        camera_entries = ingest_camera(data_dir, lat=34.05, lon=-118.25)
        satellite_entries = ingest_satellite(os.path.join(data_dir, 'satellite_data.csv'))
        sensor_entries = ingest_sensor(os.path.join(data_dir, 'sensor_logs.json'))
        
        # Fuse and analyze
        fused = fuse_streams(camera_entries, satellite_entries, sensor_entries)
        detections = detect_threats(fused)
        alerts = generate_alerts(detections)
        
        _cached_alerts = alerts
        _last_update = now
        
        return alerts
    except Exception as e:
        print(f"Error getting latest data: {e}")
        return []

@app.get("/")
async def root():
    return {"message": "FireSight AI API", "version": "1.0.0", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/alerts", response_model=List[Alert])
async def get_alerts():
    """Get current active alerts"""
    try:
        alerts = _get_latest_data()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@app.get("/data/summary", response_model=DataSummary)
async def get_data_summary():
    """Get latest fused data stream summary"""
    try:
        # Get raw data counts
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        camera_entries = ingest_camera(data_dir, lat=34.05, lon=-118.25)
        satellite_entries = ingest_satellite(os.path.join(data_dir, 'satellite_data.csv'))
        sensor_entries = ingest_sensor(os.path.join(data_dir, 'sensor_logs.json'))
        
        # Determine threat level based on alerts
        alerts = _get_latest_data()
        threat_level = "low"
        if any(alert.get("severity") == "high" for alert in alerts):
            threat_level = "high"
        elif any(alert.get("severity") == "medium" for alert in alerts):
            threat_level = "medium"
        
        return DataSummary(
            timestamp=datetime.now().isoformat(),
            total_sources=len(camera_entries) + len(satellite_entries) + len(sensor_entries),
            camera_count=len(camera_entries),
            satellite_count=len(satellite_entries),
            sensor_count=len(sensor_entries),
            threat_level=threat_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data summary: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_fire_behavior(request: PredictionRequest):
    """Mock fire behavior prediction endpoint"""
    try:
        # Simple mock prediction logic
        base_risk = 0.3
        
        # Adjust risk based on inputs
        if request.temperature and request.temperature > 30:
            base_risk += (request.temperature - 30) * 0.02
        
        if request.humidity and request.humidity < 30:
            base_risk += (30 - request.humidity) * 0.01
            
        if request.wind_speed and request.wind_speed > 10:
            base_risk += (request.wind_speed - 10) * 0.03
        
        # Cap at 1.0
        risk_score = min(base_risk, 1.0)
        
        # Determine risk level
        if risk_score > 0.7:
            risk_level = "high"
        elif risk_score > 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Mock predictions
        predicted_spread = risk_score * 5.0  # km
        time_to_spread = max(1.0, (1.0 - risk_score) * 12.0)  # hours
        
        return PredictionResponse(
            risk_level=risk_level,
            confidence=0.85,  # Mock confidence
            predicted_spread_km=round(predicted_spread, 2),
            time_to_spread_hours=round(time_to_spread, 1)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

@app.get("/alerts/types")
async def get_alert_types():
    """Get available alert types and severities"""
    return {
        "types": ["detection", "prediction", "utility"],
        "severities": ["low", "medium", "high", "critical"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
