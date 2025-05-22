from datetime import datetime, timedelta


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
