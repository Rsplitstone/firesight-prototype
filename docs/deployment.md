# FireSight AI Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ (for advanced frontend development)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rsplitstone/firesight-prototype.git
   cd firesight-prototype
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install API dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

4. **Run the backend API**
   ```bash
   cd api
   python app.py
   ```
   API will be available at `http://localhost:8000`
   
   Swagger docs available at `http://localhost:8000/docs`

5. **Serve the frontend**
   ```bash
   # Simple HTTP server for frontend
   cd frontend
   python -m http.server 3000
   ```
   Frontend will be available at `http://localhost:3000`

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     api:
       build: ./api
       ports:
         - "8000:8000"
       environment:
         - API_HOST=0.0.0.0
         - API_PORT=8000
       volumes:
         - ./data:/app/data
         - ./backend:/app/backend
     
     frontend:
       build: ./frontend
       ports:
         - "3000:80"
       depends_on:
         - api
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Individual Container Deployment

1. **Build and run API container**
   ```bash
   cd api
   docker build -t firesight-api .
   docker run -d -p 8000:8000 firesight-api
   ```

2. **Build and run frontend container**
   ```bash
   cd frontend
   docker build -t firesight-frontend .
   docker run -d -p 3000:80 firesight-frontend
   ```

## Cloud Deployment

### Option 1: Vercel (Frontend) + Fly.io (Backend)

#### Frontend on Vercel
1. Connect your GitHub repository to Vercel
2. Set build settings:
   - Framework Preset: Other
   - Build Command: `echo "Static site"`
   - Output Directory: `frontend`
3. Deploy automatically on git push

#### Backend on Fly.io
1. Install Fly CLI and authenticate
2. Create `fly.toml` in the API directory:
   ```toml
   app = "firesight-api"
   kill_signal = "SIGINT"
   kill_timeout = 5
   processes = []

   [build]
     builder = "paketobuildpacks/builder:base"

   [env]
     PORT = "8000"

   [experimental]
     allowed_public_ports = []
     auto_rollback = true

   [[services]]
     http_checks = []
     internal_port = 8000
     processes = ["app"]
     protocol = "tcp"
     script_checks = []

     [services.concurrency]
       hard_limit = 25
       soft_limit = 20
       type = "connections"

     [[services.ports]]
       force_https = true
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443

     [[services.tcp_checks]]
       grace_period = "1s"
       interval = "15s"
       restart_limit = 0
       timeout = "2s"
   ```

3. Deploy:
   ```bash
   cd api
   fly deploy
   ```

### Option 2: Heroku

#### Backend on Heroku
1. Create `Procfile` in API directory:
   ```
   web: uvicorn app:app --host=0.0.0.0 --port=${PORT:-8000}
   ```

2. Deploy:
   ```bash
   cd api
   heroku create firesight-api
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

#### Frontend on Heroku
1. Create `package.json` in frontend directory:
   ```json
   {
     "name": "firesight-frontend",
     "scripts": {
       "start": "python -m http.server $PORT"
     }
   }
   ```

2. Create `Procfile`:
   ```
   web: python -m http.server $PORT
   ```

## Environment Configuration

### Development
- `API_DEBUG=true`
- `LOG_LEVEL=DEBUG`
- `ALLOWED_ORIGINS=http://localhost:3000`

### Production
- `API_DEBUG=false`
- `LOG_LEVEL=INFO`
- `ALLOWED_ORIGINS=https://your-domain.com`
- Configure database URL
- Set up monitoring and alerting

## Monitoring and Maintenance

### Health Checks
- API health endpoint: `GET /health`
- Monitor response times and error rates
- Set up uptime monitoring

### Logging
- Structured JSON logs
- Centralized logging with ELK stack or similar
- Error tracking with Sentry

### Backup and Recovery
- Regular database backups
- Configuration backup
- Disaster recovery procedures

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify `ALLOWED_ORIGINS` environment variable
   - Check frontend URL matches allowed origins

2. **API Connection Issues**
   - Verify API is running on correct port
   - Check firewall settings
   - Validate environment variables

3. **Data Loading Errors**
   - Ensure data directory is accessible
   - Verify file permissions
   - Check data file formats

### Debug Mode
Run API in debug mode for detailed error information:
```bash
API_DEBUG=true python app.py
```

## Performance Optimization

- Enable gzip compression
- Implement response caching
- Use CDN for static assets
- Database query optimization
- Connection pooling for high traffic
