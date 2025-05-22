import json
from ingestion import ingest_camera, ingest_satellite, ingest_sensor
from fusion import fuse_streams
from analytics import detect_threats
from alert import generate_alerts


def main():
    camera_entries = ingest_camera('data', lat=34.05, lon=-118.25)
    satellite_entries = ingest_satellite('data/satellite_data.csv')
    sensor_entries = ingest_sensor('data/sensor_logs.json')

    fused = fuse_streams(camera_entries, satellite_entries, sensor_entries)
    detections = detect_threats(fused)
    alerts = generate_alerts(detections)

    print(json.dumps({"alerts": alerts}, indent=2))


if __name__ == '__main__':
    main()
