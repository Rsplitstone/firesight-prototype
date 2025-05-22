# FireSight AI Architecture

## System Overview

FireSight AI is a wildfire monitoring and early detection platform that integrates multiple data sources to provide real-time threat assessment and predictive analytics.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Ingestion     │    │   Data Fusion   │
│                 │    │   Layer         │    │   Engine        │
│ • Cameras       │───▶│                 │───▶│                 │
│ • Satellites    │    │ • Normalize     │    │ • Correlate     │
│ • IoT Sensors   │    │ • Validate      │    │ • Timestamp     │
│ • Weather APIs  │    │ • Format        │    │ • Geo-tag       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐              │
│   Frontend      │    │   REST API      │              │
│   Dashboard     │◀───│                 │              │
│                 │    │ • /alerts       │              │
│ • Live Alerts   │    │ • /data/summary │              │
│ • Maps          │    │ • /predict      │              │
│ • Analytics     │    │ • CORS Enabled  │              │
└─────────────────┘    └─────────────────┘              │
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Alert         │    │   Analytics     │
                       │   Generation    │    │   Engine        │
                       │                 │    │                 │
                       │ • Severity      │◀───│ • Rule-based    │
                       │ • Type          │    │ • ML Models     │
                       │ • Response      │    │ • Predictions   │
                       └─────────────────┘    └─────────────────┘
```

## Component Details

### 1. Data Ingestion Layer (`/backend/ingestion.py`)
- **Camera Module**: Processes image frames for smoke/flame detection
- **Satellite Module**: Ingests thermal imagery and weather data
- **IoT Sensor Module**: Collects temperature, humidity, CO2 readings
- **Unified Schema**: All data normalized to common JSON format

### 2. Data Fusion Engine (`/backend/fusion.py`)
- Temporal correlation of multi-source data
- Geospatial alignment and mapping
- Real-time stream processing simulation

### 3. Analytics Engine (`/backend/analytics.py`)
- Rule-based threat detection algorithms
- Threshold monitoring for multiple parameters
- Future: ML model integration for pattern recognition

### 4. Alert Generation (`/backend/alert.py`)
- Multi-level severity classification
- Contextual alert metadata
- Recommended response actions

### 5. REST API (`/api/app.py`)
- FastAPI-based service layer
- CORS-enabled for frontend integration
- Swagger/OpenAPI documentation
- Real-time data endpoints

### 6. Frontend Dashboard (`/frontend/index.html`)
- Interactive map interface
- Live alert feed
- Analytics visualizations
- Responsive design

## Data Flow

1. **Ingestion**: Raw data from cameras, satellites, and sensors
2. **Normalization**: Convert to unified JSON schema with timestamps and coordinates
3. **Fusion**: Correlate data points spatially and temporally
4. **Analysis**: Apply detection algorithms and prediction models
5. **Alert Generation**: Create structured alerts with severity and response recommendations
6. **API Exposure**: Serve processed data through REST endpoints
7. **Visualization**: Display real-time status on dashboard

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Frontend**: HTML5, JavaScript (ES6+), TailwindCSS
- **API**: RESTful with OpenAPI/Swagger documentation
- **Data**: JSON, CSV formats for demo data
- **Deployment**: Docker, GitHub Actions (CI/CD)

## Security Considerations

- API rate limiting (future implementation)
- Authentication and authorization (future implementation)
- Data encryption in transit
- Environment variable management
- Input validation and sanitization

## Scalability Design

- Microservices architecture ready
- Horizontal scaling support through Docker
- Database abstraction layer prepared
- Caching strategy for real-time data
- Load balancing consideration for high-traffic scenarios
