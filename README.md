# FireSight Prototype

This repository contains a simple front-end prototype and a minimal Python backend demonstrating ingestion, data fusion, basic analytics and alert generation for wildfire monitoring.

## Running the Demo Backend

1. Ensure Python 3.11 is installed.
2. From the repository root run:

```bash
python3 main.py
```

The script ingests dummy camera, satellite and sensor data from the `data/` directory, performs simple rule-based threat detection and prints generated alerts in JSON format.
