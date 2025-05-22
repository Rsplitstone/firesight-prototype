# FireSight AI Demo Guide

## Demo Overview
This guide walks through a complete demonstration of the FireSight AI wildfire monitoring platform, showcasing core functionality for early detection, data fusion, and alert generation.

## Demo Scenario: Simulated Fire Event

### Setup (2 minutes)

1. **Start the system**
   ```bash
   # Terminal 1: Start API
   cd api
   python app.py
   
   # Terminal 2: Start frontend
   cd frontend
   python -m http.server 3000
   ```

2. **Open the dashboard**
   - Navigate to `http://localhost:3000`
   - API documentation available at `http://localhost:8000/docs`

### Demo Script (10 minutes)

#### Part 1: Dashboard Overview (2 minutes)
1. **Show the main dashboard**
   - Point out the sidebar navigation
   - Highlight the Regional Overview Map
   - Show the Recent Alerts section (initially may show "Loading alerts...")

2. **Explain the interface**
   - "This is FireSight AI's real-time wildfire monitoring dashboard"
   - "We integrate multiple data sources: cameras, satellites, and IoT sensors"
   - "The system provides early detection and predictive modeling"

#### Part 2: Live Data Ingestion (3 minutes)
1. **Navigate to Early Detection section**
   - Click "Early Detection" in sidebar
   - Show the Detection Map with zones
   - Point out different sensor types (CAM1, IoT3, SAT2)

2. **Trigger live data processing**
   ```bash
   # In terminal, run the backend
   cd backend
   python main.py
   ```
   
3. **Show API in action**
   - Open `http://localhost:8000/docs`
   - Demonstrate GET `/alerts` endpoint
   - Show GET `/data/summary` endpoint
   - Explain the real-time data structure

#### Part 3: Alert Generation (3 minutes)
1. **Generate alerts through API**
   ```bash
   # Use curl to test prediction endpoint
   curl -X POST "http://localhost:8000/predict" \
        -H "Content-Type: application/json" \
        -d '{
          "lat": 34.05,
          "lon": -118.25,
          "temperature": 45,
          "humidity": 15,
          "wind_speed": 25
        }'
   ```

2. **Show alert classification**
   - Explain severity levels (low, medium, high, critical)
   - Show how multiple data sources trigger alerts
   - Demonstrate geographic correlation

#### Part 4: Predictive Modeling (2 minutes)
1. **Navigate to Prediction Modeling**
   - Show fire spread prediction visualization
   - Explain the concentric circles (1hr, 3hr, 6hr predictions)
   - Point out environmental factors

2. **Interactive prediction**
   - Use the `/predict` API endpoint with different parameters
   - Show how changing conditions affects risk assessment

## Demo Data Explanation

### Sample Fire Scenario
The demo uses a realistic fire scenario with:

- **Location**: Los Angeles area (34.05°N, 118.25°W)
- **Weather conditions**: High temperature (45°C), low humidity (15%), strong winds (25 mph)
- **Multiple detection sources**:
  - Thermal satellite imagery showing temperature anomaly
  - Camera system detecting visual smoke/flame signatures
  - IoT sensors reporting elevated CO2 and temperature

### Data Sources Demonstrated

1. **Camera Feed** (`data/frame1.jpg`)
   - Simulates visual detection capability
   - Timestamped and geo-tagged

2. **Satellite Data** (`data/satellite_data.csv`)
   - Thermal readings across geographic grid
   - Shows temperature anomalies indicating potential ignition

3. **IoT Sensor Network** (`data/sensor_logs.json`)
   - Environmental monitoring data
   - Temperature, humidity, CO2 concentrations

## Key Demo Points to Highlight

### 1. Multi-Modal Detection
- "FireSight doesn't rely on a single source—we fuse camera, satellite, and sensor data"
- "This redundancy reduces false positives and increases detection confidence"

### 2. Real-Time Processing
- "Data flows through our system in near real-time"
- "Alerts are generated within seconds of detection"

### 3. Intelligent Analytics
- "Our rule-based system correlates multiple indicators"
- "Temperature spikes + visual detection + environmental conditions = high-confidence alert"

### 4. Predictive Capabilities
- "Beyond just detection, we predict fire behavior"
- "Wind patterns, terrain, and fuel load all factor into spread modeling"

### 5. Actionable Intelligence
- "Every alert includes severity, location, and recommended response"
- "Integration ready for emergency response systems"

## Technical Deep Dive (For Technical Audiences)

### Architecture Highlights
1. **Microservices Design**
   - Separate ingestion, fusion, analytics, and alert services
   - RESTful API for integration flexibility

2. **Data Pipeline**
   ```
   Raw Data → Ingestion → Fusion → Analytics → Alerts → API → Dashboard
   ```

3. **Scalability Features**
   - Stateless API design
   - Docker containerization ready
   - Horizontal scaling capabilities

### API Demonstration
Show live API calls and responses:

```bash
# Get current system status
curl http://localhost:8000/health

# Retrieve active alerts
curl http://localhost:8000/alerts

# Get data summary
curl http://localhost:8000/data/summary

# Test prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"lat": 34.05, "lon": -118.25, "temperature": 50}'
```

## Demo Troubleshooting

### Common Issues
1. **"Loading alerts..." doesn't update**
   - Check API is running on port 8000
   - Verify CORS settings allow localhost:3000

2. **API endpoints return errors**
   - Ensure data files exist in `/data` directory
   - Check Python dependencies are installed

3. **Map visualization issues**
   - Refresh browser page
   - Check console for JavaScript errors

### Quick Fixes
```bash
# Restart API
cd api && python app.py

# Regenerate demo data
cd scripts
python generate_demo_dataset.py ../data/demo_dataset.csv

# Check API health
curl http://localhost:8000/health
```

## Demo Customization

### Adjusting Scenario Parameters
Edit demo data files to create different scenarios:

1. **Increase severity**: Modify `satellite_data.csv` with higher thermal readings
2. **Change location**: Update coordinates in ingestion scripts
3. **Add more sensors**: Extend `sensor_logs.json` with additional data points

### Creating New Scenarios
Use the demo data generator:
```bash
cd scripts
python generate_demo_dataset.py custom_scenario.csv
python replay_fire_scenario.py custom_scenario.csv
```

## Post-Demo Discussion Points

### Current Capabilities
- Multi-source data ingestion and fusion
- Rule-based threat detection
- Real-time alert generation
- RESTful API for integration
- Interactive dashboard visualization

### Future Roadmap
- Machine learning model integration
- Real-time camera stream processing
- Integration with NASA FIRMS API
- SMS/email alert notifications
- Advanced fire behavior modeling
- Mobile app for field personnel

### Business Value Proposition
- **Early Detection**: Minutes matter in wildfire response
- **Reduced False Positives**: Multi-source validation increases accuracy
- **Actionable Intelligence**: Not just alerts, but recommended responses
- **Integration Ready**: API-first design for existing emergency systems
- **Scalable Platform**: Designed for growth from pilot to enterprise
