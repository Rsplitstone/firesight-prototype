import os
import csv
import json
from datetime import datetime


UNIFIED_SCHEMA_FIELDS = ["source", "timestamp", "lat", "lon", "data"]

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
            "lat": rec["lat"],
            "lon": rec["lon"],
            "data": {
                "temperature": rec["temperature"],
                "humidity": rec["humidity"]
            }
        }
        entries.append(entry)
    return entries
