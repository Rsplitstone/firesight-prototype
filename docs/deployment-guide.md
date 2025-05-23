# FireSight AI Deployment Guide

This guide covers deploying the FireSight AI platform for wildfire detection and monitoring.

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: At least 10GB free space
- **Network**: Internet connection for satellite data APIs

### Required Software
1. **Docker Desktop** (includes Docker Compose)
   - Windows/Mac: Download from [docker.com](https://www.docker.com/products/docker-desktop)
   - Linux: Install Docker Engine and Docker Compose separately

2. **Git** (for cloning and updates)
   - Download from [git-scm.com](https://git-scm.com/)

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Rsplitstone/firesight-prototype.git
cd firesight-prototype
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Add your NASA API key and other settings
```

### 3. Deploy with Scripts

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Linux/macOS (Bash):**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/health

## Manual Deployment

If you prefer manual deployment or need to customize the process:

### 1. Build Images
```bash
docker compose build
```

### 2. Start Services
```bash
docker compose up -d
```

### 3. View Logs
```bash
docker compose logs -f
```

### 4. Stop Services
```bash
docker compose down
```

## Configuration

### Environment Variables

Edit the `.env` file to customize your deployment:

```bash
# NASA API Key (required for satellite data)
NASA_API_KEY=your_nasa_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Logging
LOG_LEVEL=INFO

# External Services
WEATHER_API_KEY=your_weather_api_key_here
```

### NASA API Key Setup

1. Visit [NASA FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/area/)
2. Register for a free API key
3. Add the key to your `.env` file

## Service Architecture

The deployment includes the following services:

### Backend Service
- **Purpose**: Satellite data ingestion and processing
- **Port**: Internal only
- **Health Check**: Python import test

### API Service
- **Purpose**: REST API for frontend and external integrations
- **Port**: 8000 (external)
- **Health Check**: HTTP health endpoint

### Frontend Service
- **Purpose**: Web interface for monitoring and visualization
- **Port**: 3000 (external)
- **Technology**: Static HTML/JS served by Nginx

### Redis Service
- **Purpose**: Caching and task queue
- **Port**: 6379 (internal)
- **Data**: Persistent volume

## Monitoring and Maintenance

### Health Checks
All services include health checks that run every 30 seconds:
```bash
# Check service status
docker compose ps

# View health check logs
docker compose logs <service_name>
```

### Log Management
```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs backend
docker compose logs api

# Follow logs in real-time
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100
```

### Data Persistence
- Redis data is stored in a named volume
- Application logs are stored in `./backend/logs/`
- Processed data is stored in `./data/`

## Scaling and Performance

### Horizontal Scaling
To run multiple instances of a service:
```bash
docker compose up -d --scale backend=3 --scale api=2
```

### Resource Limits
Add resource constraints to `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8000

# Use different ports in .env or docker-compose.yml
```

#### 2. Permission Denied
```bash
# On Linux, ensure Docker daemon is running
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 3. Out of Memory
```bash
# Clean up unused containers and images
docker system prune -a

# Increase Docker Desktop memory allocation
```

#### 4. API Key Issues
- Verify NASA API key in `.env` file
- Check API key quotas and limits
- Test API key with direct curl request

### Debug Mode
Enable debug mode for detailed logging:
```bash
# Set in .env file
API_DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
docker compose restart
```

## Security Considerations

### Production Deployment
For production environments:

1. **Change default passwords** in `.env`
2. **Use HTTPS** with SSL certificates
3. **Configure firewall** rules
4. **Regular updates** with `git pull && docker compose build`
5. **Monitor logs** for suspicious activity
6. **Backup data** regularly

### Network Security
```yaml
# Add to docker-compose.yml for production
networks:
  firesight-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## CI/CD Integration

The project includes GitHub Actions for automated testing and deployment:

- **Testing**: Runs on every push and PR
- **Building**: Creates Docker images
- **Deployment**: Can be extended for cloud platforms

See `.github/workflows/python-app.yml` for configuration.

## Cloud Deployment

### AWS
Use AWS ECS or EKS with the provided Docker images.

### Google Cloud
Deploy to Google Cloud Run or GKE.

### Azure
Use Azure Container Instances or AKS.

### DigitalOcean
Deploy to DigitalOcean App Platform or Kubernetes.

## Support

For issues and questions:
1. Check this deployment guide
2. Review application logs
3. Check GitHub Issues
4. Create a new issue with logs and configuration details
