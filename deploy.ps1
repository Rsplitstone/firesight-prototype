# FireSight Deployment Script for Windows
# This script helps deploy the FireSight AI platform on Windows

Write-Host "🔥 FireSight AI Deployment Script" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please update Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env file with your actual API keys and configuration." -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "data\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\logs" | Out-Null

# Pull latest changes (if this is a git repository)
if (Test-Path ".git") {
    Write-Host "📥 Pulling latest changes..." -ForegroundColor Cyan
    git pull origin main
}

# Build and start services
Write-Host "🏗️  Building Docker images..." -ForegroundColor Cyan
docker compose build --no-cache

Write-Host "🚀 Starting FireSight services..." -ForegroundColor Cyan
docker compose up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
docker compose ps

# Show logs
Write-Host ""
Write-Host "📋 Recent logs:" -ForegroundColor Cyan
docker compose logs --tail=20

Write-Host ""
Write-Host "✅ FireSight deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   API: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "📊 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker compose logs -f" -ForegroundColor White
Write-Host "   Stop services: docker compose down" -ForegroundColor White
Write-Host "   Restart: docker compose restart" -ForegroundColor White
Write-Host "   Update: git pull; docker compose build; docker compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "⚙️  Configuration:" -ForegroundColor Cyan
Write-Host "   Edit .env file to customize settings" -ForegroundColor White
Write-Host "   Add your NASA API key for satellite data access" -ForegroundColor White
