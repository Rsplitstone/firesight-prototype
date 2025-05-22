"""
Unit tests for FireSight AI backend components
"""

import pytest
import json
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ingestion import ingest_camera, ingest_satellite, ingest_sensor
from fusion import fuse_streams
from analytics import detect_threats
from alert import generate_alerts


class TestIngestion:
    """Test data ingestion modules"""
    
    def test_camera_ingestion_structure(self):
        """Test camera data ingestion returns correct structure"""
        # Create a temporary test directory with a dummy image
        test_data = ingest_camera('../data', lat=34.05, lon=-118.25)
        
        assert isinstance(test_data, list)
        if test_data:  # If there are images in the data directory
            entry = test_data[0]
            assert 'source' in entry
            assert 'timestamp' in entry
            assert 'lat' in entry
            assert 'lon' in entry
            assert 'data' in entry
            assert entry['source'] == 'camera'
    
    def test_satellite_ingestion_structure(self):
        """Test satellite data ingestion returns correct structure"""
        test_data = ingest_satellite('../data/satellite_data.csv')
        
        assert isinstance(test_data, list)
        if test_data:  # If the CSV file exists and has data
            entry = test_data[0]
            assert 'source' in entry
            assert 'timestamp' in entry
            assert 'lat' in entry
            assert 'lon' in entry
            assert 'data' in entry
            assert entry['source'] == 'satellite'
    
    def test_sensor_ingestion_structure(self):
        """Test sensor data ingestion returns correct structure"""
        test_data = ingest_sensor('../data/sensor_logs.json')
        
        assert isinstance(test_data, list)
        if test_data:  # If the JSON file exists and has data
            entry = test_data[0]
            assert 'source' in entry
            assert 'timestamp' in entry
            assert 'lat' in entry
            assert 'lon' in entry
            assert 'data' in entry
            assert entry['source'] == 'sensor'


class TestFusion:
    """Test data fusion functionality"""
    
    def test_fuse_streams_combines_data(self):
        """Test that fusion combines multiple data streams"""
        camera_data = [{'source': 'camera', 'timestamp': '2023-01-01T00:00:00Z', 'lat': 34.0, 'lon': -118.0, 'data': {}}]
        satellite_data = [{'source': 'satellite', 'timestamp': '2023-01-01T00:01:00Z', 'lat': 34.0, 'lon': -118.0, 'data': {}}]
        sensor_data = [{'source': 'sensor', 'timestamp': '2023-01-01T00:02:00Z', 'lat': 34.0, 'lon': -118.0, 'data': {}}]
        
        fused = fuse_streams(camera_data, satellite_data, sensor_data)
        
        assert isinstance(fused, list)
        assert len(fused) == 3
        sources = [entry['source'] for entry in fused]
        assert 'camera' in sources
        assert 'satellite' in sources
        assert 'sensor' in sources


class TestAnalytics:
    """Test analytics and threat detection"""
    
    def test_detect_threats_high_temperature(self):
        """Test threat detection with high temperature scenario"""
        test_data = [
            {
                'source': 'satellite',
                'timestamp': '2023-01-01T12:00:00Z',
                'lat': 34.05,
                'lon': -118.25,
                'data': {'thermal': 75}  # High thermal reading
            },
            {
                'source': 'sensor',
                'timestamp': '2023-01-01T12:01:00Z',
                'lat': 34.05,
                'lon': -118.25,
                'data': {'temperature': 55}  # High temperature
            }
        ]
        
        threats = detect_threats(test_data)
        assert isinstance(threats, list)
        # Should detect threat due to high thermal + high temperature
        assert len(threats) > 0
    
    def test_detect_threats_low_temperature(self):
        """Test threat detection with normal temperature scenario"""
        test_data = [
            {
                'source': 'satellite',
                'timestamp': '2023-01-01T12:00:00Z',
                'lat': 34.05,
                'lon': -118.25,
                'data': {'thermal': 25}  # Normal thermal reading
            },
            {
                'source': 'sensor',
                'timestamp': '2023-01-01T12:01:00Z',
                'lat': 34.05,
                'lon': -118.25,
                'data': {'temperature': 20}  # Normal temperature
            }
        ]
        
        threats = detect_threats(test_data)
        assert isinstance(threats, list)
        # Should not detect threat with normal readings
        assert len(threats) == 0


class TestAlerts:
    """Test alert generation"""
    
    def test_generate_alerts_structure(self):
        """Test alert generation returns correct structure"""
        test_detections = [
            {
                'type': 'detection',
                'severity': 'high',
                'timestamp': '2023-01-01T12:00:00Z',
                'lat': 34.05,
                'lon': -118.25,
                'details': {'thermal': 75, 'temperature': 55}
            }
        ]
        
        alerts = generate_alerts(test_detections)
        
        assert isinstance(alerts, list)
        if alerts:  # If alerts are generated
            alert = alerts[0]
            assert 'type' in alert
            assert 'severity' in alert
            assert 'timestamp' in alert
            assert 'lat' in alert
            assert 'lon' in alert


class TestIntegration:
    """Integration tests for full pipeline"""
    
    def test_full_pipeline_with_real_data(self):
        """Test complete pipeline with actual demo data"""
        try:
            # Test ingestion
            camera_entries = ingest_camera('../data', lat=34.05, lon=-118.25)
            satellite_entries = ingest_satellite('../data/satellite_data.csv')
            sensor_entries = ingest_sensor('../data/sensor_logs.json')
            
            # Test fusion
            fused = fuse_streams(camera_entries, satellite_entries, sensor_entries)
            
            # Test analytics
            detections = detect_threats(fused)
            
            # Test alert generation
            alerts = generate_alerts(detections)
            
            # Verify pipeline completed without errors
            assert isinstance(fused, list)
            assert isinstance(detections, list)
            assert isinstance(alerts, list)
            
        except FileNotFoundError:
            pytest.skip("Demo data files not found - skipping integration test")


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])
