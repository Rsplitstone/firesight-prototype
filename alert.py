def generate_alerts(detections):
    """Create final alert JSON objects from detections."""
    alerts = []
    for idx, det in enumerate(detections, start=1):
        recommendation = (
            "Immediate response required" if det["severity"] == "high" else "Monitor situation"
        )
        alert = {
            "id": f"alert-{idx}",
            "type": det["type"],
            "severity": det["severity"],
            "time": det["timestamp"],
            "location": {"lat": det["lat"], "lon": det["lon"]},
            "recommended_response": recommendation,
            "details": det["details"],
        }
        alerts.append(alert)
    return alerts
