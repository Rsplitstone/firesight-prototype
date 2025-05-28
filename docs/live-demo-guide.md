# 🔥 FireSight AI - Live Demo Deployment Guide

## 🚀 Quick Start (Recommended)

The fastest way to get your FireSight live demo running:

### 1. Clone and Setup
```bash
git clone https://github.com/Rsplitstone/firesight-prototype.git
cd firesight-prototype
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your NASA API key
# Required: NASA_API_KEY=your_actual_api_key_here
```

### 3. Deploy Live Demo

**Windows:**
```powershell
.\deploy-live-demo.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy-live-demo.sh
./deploy-live-demo.sh
```

### 4. Access Your Live Demo
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🌐 Deployment Options

### Option 1: Local Development Demo
Perfect for development and testing:
```bash
docker compose up -d
```

### Option 2: Production-Ready Demo
Enhanced with nginx, database, and monitoring:
```bash
docker compose -f docker-compose.production.yml --profile production up -d
```

### Option 3: Cloud Deployment
Deploy to cloud platforms like AWS, Azure, or DigitalOcean.

---

## 🔧 Configuration

### Required Environment Variables
```env
# NASA API Key (Required)
NASA_API_KEY=your_nasa_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./firesight.db

# Cache
REDIS_URL=redis://redis:6379
```

### Getting NASA API Key
1. Visit: https://firms.modaps.eosdis.nasa.gov/api/area/
2. Register for free account
3. Generate API key
4. Add to your `.env` file

---

## 📱 Demo Features

Your live demo includes:

### 🛰️ Real-Time Satellite Data
- NASA MODIS fire detection
- VIIRS satellite imagery
- GOES weather data
- Live fire perimeter tracking

### 🤖 AI-Powered Detection
- Machine learning fire detection
- Risk assessment algorithms
- Predictive fire modeling
- Multi-sensor data fusion

### 📊 Interactive Dashboard
- Real-time fire map
- Risk heatmaps  
- Alert management
- Data visualization

### 🚨 Alert System
- Email notifications
- SMS alerts (with Twilio)
- Webhook integrations
- Custom alert rules

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│      API        │────│    Backend      │
│   (Dashboard)   │    │   (FastAPI)     │    │   (Processing)  │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Caching)     │
                    │   Port: 6379    │
                    └─────────────────┘
```

---

## 🔍 Testing Your Demo

### 1. Health Checks
```bash
# API Health
curl http://localhost:8000/health

# Frontend Health  
curl http://localhost:3000/health
```

### 2. NASA API Test
```bash
# Test NASA API connectivity
docker compose exec backend python test_nasa_api.py
```

### 3. End-to-End Test
```bash
# Run full test suite
docker compose exec backend python -m pytest test_satellite_integration.py
```

---

## 📈 Monitoring

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f backend
```

### Performance Monitoring
- API metrics at `/metrics` endpoint
- Redis monitoring via RedisInsight
- Container stats with `docker stats`

---

## 🚀 Cloud Deployment

### AWS EC2
1. Launch EC2 instance (t3.medium recommended)
2. Install Docker and Docker Compose
3. Clone repository and configure
4. Run deployment script
5. Configure security groups for ports 80, 443

### DigitalOcean Droplet
1. Create droplet with Docker
2. Follow standard deployment steps
3. Configure domain and SSL

### Azure Container Instances
1. Use azure-deployment.yml (if provided)
2. Configure Azure Container Registry
3. Deploy via Azure CLI

---

## 🔒 Security Considerations

### Production Checklist
- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging
- [ ] Regular security updates
- [ ] API rate limiting
- [ ] Input validation

### Environment Security
```env
# Use strong passwords
DB_PASSWORD=strong_random_password
SECRET_KEY=random_secret_key

# Restrict CORS origins
ALLOWED_ORIGINS=https://yourdomain.com

# Enable security headers
SECURITY_HEADERS=true
```

---

## 🛠️ Troubleshooting

### Common Issues

**Docker Issues:**
```bash
# Clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

**API Not Responding:**
```bash
# Check API logs
docker compose logs api

# Check if port is available
netstat -an | grep 8000
```

**NASA API Errors:**
```bash
# Verify API key
grep NASA_API_KEY .env

# Test connectivity
docker compose exec backend python test_nasa_api.py
```

### Performance Optimization
- Increase Docker memory allocation
- Use Redis for caching
- Enable gzip compression
- Optimize database queries

---

## 📞 Support

### Documentation
- [Architecture Guide](docs/architecture.md)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](docs/deployment-guide.md)

### Community
- GitHub Issues: https://github.com/Rsplitstone/firesight-prototype/issues
- Discussions: https://github.com/Rsplitstone/firesight-prototype/discussions

---

## 🎯 Next Steps

After your demo is running:

1. **Customize Dashboard** - Modify frontend for your needs
2. **Add Data Sources** - Integrate additional sensors
3. **Enhance AI Models** - Improve detection algorithms  
4. **Scale Deployment** - Add load balancing, monitoring
5. **Mobile App** - Create mobile interface
6. **Integration** - Connect with existing systems

---

**🔥 Your FireSight AI live demo is ready to showcase wildfire detection capabilities!**
