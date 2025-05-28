# 🔥 FireSight AI - Live Demo Ready! 

## 🎯 **YOUR LIVE DEMO IS READY TO DEPLOY** 

### 🚀 One-Command Deployment

**Windows (Recommended):**
```powershell
.\deploy-live-demo.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy-live-demo.sh
./deploy-live-demo.sh
```

---

## 🌐 Live Demo Access Points

Once deployed, your live demo will be available at:

| Service | URL | Description |
|---------|-----|-------------|
| **🎮 Live Dashboard** | http://localhost:3000 | Interactive wildfire monitoring dashboard |
| **🔌 API Endpoint** | http://localhost:8000 | REST API for data access |
| **📋 API Documentation** | http://localhost:8000/docs | Auto-generated API docs |
| **📊 Demo Status** | http://localhost:8000/demo/status | System health and status |
| **🛰️ Live Satellite Data** | http://localhost:8000/demo/satellite-data | Real NASA satellite feeds |
| **🔥 Fire Simulation** | http://localhost:8000/demo/fire-simulation | Interactive fire spread demo |
| **📈 Live Metrics** | http://localhost:8000/demo/metrics | Performance metrics |

---

## 🛠️ What Your Demo Includes

### 🎮 **Interactive Features**
- ✅ Real-time wildfire detection simulation
- ✅ NASA satellite data integration (MODIS, VIIRS)
- ✅ Interactive fire spread modeling
- ✅ Live performance metrics
- ✅ Alert system demonstration
- ✅ Multi-sensor data fusion

### 🛰️ **Live Data Sources**
- ✅ **NASA FIRMS API** - Active fire detection
- ✅ **MODIS Collection 6.1** - Thermal anomaly detection
- ✅ **VIIRS I-Band** - High-resolution fire data
- ✅ **Weather Integration** - Wind, humidity, temperature
- ✅ **Mock Camera Feeds** - Simulated camera detection

### 🏗️ **Technical Stack**
- ✅ **Frontend**: Interactive HTML5 dashboard with Tailwind CSS
- ✅ **API**: FastAPI with automatic documentation
- ✅ **Backend**: Python data processing with NASA API integration
- ✅ **Database**: Redis for caching and session management
- ✅ **Deployment**: Docker Compose with health checks

---

## 🔑 Pre-Configured Components

### ✅ **NASA API Integration**
- **API Key**: `bdf26045c9cb1b8129d98cb0e84b40f4` (5000 calls/10 min)
- **Endpoint**: NASA FIRMS fire detection data
- **Coverage**: Global real-time fire detection
- **Fallback**: Demo data if API unavailable

### ✅ **Environment Configuration**
```env
NASA_API_KEY=bdf26045c9cb1b8129d98cb0e84b40f4
API_HOST=0.0.0.0
API_PORT=8000
REDIS_URL=redis://redis:6379
DATABASE_URL=sqlite:///./firesight.db
```

### ✅ **Docker Services**
- **Frontend**: Nginx-served dashboard (Port 3000)
- **API**: FastAPI application (Port 8000)  
- **Backend**: Python processing engine
- **Redis**: Caching and sessions (Port 6379)

---

## 🚀 Deployment Options

### Option 1: **Quick Demo** (Default)
```bash
.\deploy-live-demo.ps1
```
- Single command deployment
- All services in Docker
- Auto health checks
- Browser auto-opens

### Option 2: **Production Demo**
```bash
docker compose -f docker-compose.production.yml --profile production up -d
```
- Includes nginx reverse proxy
- PostgreSQL database
- SSL-ready configuration
- Production monitoring

### Option 3: **Development Mode**
```bash
# API only
cd api && python app.py

# Frontend only  
cd frontend && python -m http.server 3000
```

---

## 🎯 Demo Scenarios

### **Scenario 1: Live Fire Detection**
1. Open dashboard at http://localhost:3000
2. View real-time fire detection map
3. Watch NASA satellite data updates
4. See alert generation in action

### **Scenario 2: Fire Spread Simulation**
1. Navigate to fire simulation section
2. Watch predictive fire spread modeling
3. Adjust parameters (wind, humidity)
4. See evacuation zone recommendations

### **Scenario 3: API Integration Demo**
1. Open http://localhost:8000/docs
2. Test API endpoints interactively
3. View real satellite data responses
4. Integrate with external systems

---

## 🔧 Management Commands

```bash
# View all service logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f backend

# Restart services
docker compose restart

# Stop demo
docker compose down

# Clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Monitoring Your Demo

### **Health Checks**
```bash
# API health
curl http://localhost:8000/health

# Demo system status
curl http://localhost:8000/demo/status

# Live metrics
curl http://localhost:8000/demo/metrics
```

### **NASA API Testing**
```bash
# Test NASA API connectivity
docker compose exec backend python test_nasa_api.py
```

---

## 🎥 **Demo Presentation Points**

### **1. Real-Time Capability** 
- Show live NASA satellite data integration
- Demonstrate sub-minute detection times
- Display confidence scoring and validation

### **2. AI-Powered Intelligence**
- Fire spread prediction algorithms
- Risk assessment and scoring
- Resource optimization recommendations

### **3. Multi-Source Integration**
- Satellite imagery (MODIS, VIIRS)
- Weather data integration
- IoT sensor simulation
- Camera feed processing

### **4. Scalable Architecture**
- Microservices design
- Docker containerization
- REST API for integrations
- Cloud-ready deployment

---

## 🚀 **Next Steps for Production**

1. **🌐 Cloud Deployment**
   - Deploy to AWS/Azure/GCP
   - Configure domain and SSL
   - Set up CDN for global access

2. **📱 Mobile Integration**
   - Build mobile app
   - Push notifications
   - Offline capabilities

3. **🔧 Enterprise Features**
   - User authentication
   - Role-based access
   - Advanced analytics
   - Custom integrations

4. **📈 Scaling**
   - Load balancing
   - Database clustering
   - Monitoring & logging
   - Performance optimization

---

## 🎉 **YOU'RE READY TO DEMO!**

Your FireSight AI live demo is fully configured and ready to showcase:

1. **Run**: `.\deploy-live-demo.ps1`
2. **Open**: http://localhost:3000
3. **Present**: Real-time wildfire detection capabilities
4. **Impress**: Stakeholders with live NASA data integration

**🔥 Demonstrate the future of wildfire detection technology!**
