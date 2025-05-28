# 🔥 FireSight AI - Live Demo Ready!

> **🎯 [LIVE DEMO DEPLOYMENT GUIDE](LIVE_DEMO_READY.md) - Deploy in 2 minutes!**

**Deploy your live demo now:**
```powershell
# Windows (One command deployment)
.\deploy-live-demo.ps1

# Then open: http://localhost:3000 🚀
```

---

🚀 **[DEPLOYMENT COMPLETE!](DEPLOYMENT_COMPLETE.md)** - Enhanced with NASA satellite data integration

## 🔥 Quick Start - Live Demo

**Get your live demo running in 2 minutes:**

```bash
# 1. Clone the repository
git clone https://github.com/Rsplitstone/firesight-prototype.git
cd firesight-prototype

# 2. Deploy live demo (Windows)
.\deploy-live-demo.ps1

# OR Deploy live demo (Linux/Mac)
chmod +x deploy-live-demo.sh
./deploy-live-demo.sh
```

**Then open:** http://localhost:3000 🎯

---

This repository contains a functional prototype for the FireSight AI platform that demonstrates core wildfire detection and monitoring capabilities. It integrates diverse data sources including camera feeds, satellite imagery, IoT sensors, and weather data, then uses AI analytics to detect and predict fire incidents. The system includes a proper architecture with API endpoints for integration and a web-based dashboard for visualization.

## Features

- **🎮 Live Interactive Demo**: Complete dashboard with real-time data visualization
- **🛰️ Enhanced satellite data**: MODIS Collection 6.1, VIIRS I-Band (Suomi NPP & NOAA-20), combined products
- **🔗 NASA FIRMS API integration**: Real-time access to active fire detection data with configured API key
- **📡 Comprehensive satellite sources**: MODIS, VIIRS, GOES, Sentinel, Landsat, and more
- **🤖 AI-powered analytics**: Fire detection, spread prediction, and resource optimization
- **⚡ Real-time monitoring**: Continuous observation with rapid alert generation
- **📊 Interactive dashboard**: Visualization of fire incidents, predictions, and resources
- **🔌 REST API**: Well-documented endpoints for easy integration with other systems
- **🐳 Docker deployment**: Production-ready containerized services
- **⚙️ CI/CD pipeline**: Automated testing and deployment workflows

## Running the Demo Backend

1. Ensure Python 3.11 is installed.
2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Run the basic demo:

```bash
python3 main.py
```

4. For comprehensive analysis with all satellite data sources:

```bash
python3 backend/satellite_coordinator.py
```

The system ingests camera frames, satellite data, IoT sensor readings, and weather information, performs AI-based fire detection, and generates alerts with severity and confidence ratings.

## Demo Data Scripts

The `scripts` directory contains two helper utilities:

- `generate_demo_dataset.py` – creates a 24‑hour CSV file with simulated sensor readings and a fire ignition event around noon.
- `replay_fire_scenario.py` – prints dataset rows to the console in sequence so the scenario can be replayed quickly for demos.

### Dataset format

The generated CSV has the following columns:

| column | description |
| --- | --- |
| `timestamp` | ISO‑8601 timestamp for each minute of the day |
| `temperature_c` | temperature in Celsius |
| `humidity_pct` | relative humidity percentage |
| `co2_ppm` | CO₂ concentration in ppm |
| `smoke` | `0` or `1` to indicate smoke detection |
| `flame` | `0` or `1` to indicate flame detection |

The ignition event increases temperature and CO₂ while setting both `smoke` and `flame` to `1` for approximately 15 minutes.

To create the dataset run:

```bash
python3 scripts/generate_demo_dataset.py demo_dataset.csv
```

Then replay it with:

```bash
python3 scripts/replay_fire_scenario.py demo_dataset.csv
```

## Satellite Data Integration

FireSight integrates multiple satellite data sources for comprehensive wildfire detection:

| Source | Description | Resolution | Update Frequency |
| ------ | ----------- | ---------- | ---------------- |
| NASA FIRMS | Fire Information for Resource Management System | 375m | 3h - NRT, Daily - SP |
| MODIS Collection 6.1 | Active fire detection product | 1km | 2x daily |
| VIIRS I-Band | Active fire products from SNPP and NOAA-20 | 375m | 12h |
| GOES-16/17 | ABI Fire/Hot-Spot Characterization | 2km | 5-15 min |
| Additional Sources | Sentinel-2, Landsat, NIFC Perimeters, IRWIN Incidents | Various | Various |

To test satellite data integration:

```bash
python3 backend/test_satellite_integration.py
```

For detailed information about satellite data sources, see [Satellite Data Integration Guide](docs/satellite_data_integration.md).

## 🚀 Live Demo Access

After deployment, access these URLs:

- **🌐 Live Dashboard**: http://localhost:3000
- **🔌 API Endpoint**: http://localhost:8000  
- **📋 API Documentation**: http://localhost:8000/docs
- **📊 Demo Status**: http://localhost:8000/demo/status
- **🛰️ Live Satellite Data**: http://localhost:8000/demo/satellite-data

## Quick Deployment

### Using Deployment Scripts (Recommended)

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Linux/macOS (Bash):**
```bash
chmod +x deploy.sh && ./deploy.sh
```

### Manual Docker Deployment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your NASA API key and configuration

# Build and start services
docker compose build
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

## 📖 Documentation

- **[Live Demo Guide](docs/live-demo-guide.md)** - Complete deployment guide
- **[Demo Guide](docs/demo-guide.md)** - Basic usage instructions
- **[Deployment Guide](docs/deployment-guide.md)** - Advanced deployment options
- **[Architecture](docs/architecture.md)** - System architecture details

---
