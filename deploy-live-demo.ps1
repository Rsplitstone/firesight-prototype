# FireSight AI - Live Demo Deployment Script (Windows)
# This script sets up a complete live demo environment on Windows

Write-Host "🔥 FireSight AI - Live Demo Deployment" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Yellow

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: docker-compose.yml not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Setup environment
Write-Host "📋 Setting up environment..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env from .env.example" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env file with your actual API keys before continuing." -ForegroundColor Yellow
        Write-Host "   Required: NASA_API_KEY" -ForegroundColor White
        Write-Host "   Press Enter after editing .env file..." -ForegroundColor White
        Read-Host
    } else {
        Write-Host "❌ Error: .env.example not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Validate NASA API key
Write-Host "🛰️ Validating NASA API configuration..." -ForegroundColor Cyan
$envContent = Get-Content ".env" -Raw
if ($envContent -match "NASA_API_KEY=([^`r`n]+)") {
    $nasaKey = $matches[1]
    if ($nasaKey -eq "your_nasa_api_key_here" -or [string]::IsNullOrEmpty($nasaKey)) {
        Write-Host "❌ Error: Please configure your NASA API key in .env file" -ForegroundColor Red
        Write-Host "   Get your free key at: https://firms.modaps.eosdis.nasa.gov/api/area/" -ForegroundColor White
        exit 1
    }
    Write-Host "✅ NASA API key configured" -ForegroundColor Green
} else {
    Write-Host "❌ Error: NASA_API_KEY not found in .env file" -ForegroundColor Red
    exit 1
}

# Create required directories
Write-Host "📁 Creating required directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "backend\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null
Write-Host "✅ Directories created" -ForegroundColor Green

# Build and start services
Write-Host "🐳 Building Docker containers..." -ForegroundColor Cyan
docker compose build --no-cache

Write-Host "🚀 Starting FireSight demo services..." -ForegroundColor Cyan
docker compose up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
$healthCheckAttempts = 0
$maxAttempts = 30

do {
    $healthCheckAttempts++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API service is healthy" -ForegroundColor Green
            break
        }
    } catch {
        if ($healthCheckAttempts -eq $maxAttempts) {
            Write-Host "❌ API service failed to start properly" -ForegroundColor Red
            Write-Host "Showing API logs:" -ForegroundColor Yellow
            docker compose logs api
            exit 1
        }
        Start-Sleep -Seconds 2
    }
} while ($healthCheckAttempts -lt $maxAttempts)

# Test NASA API connectivity
Write-Host "🛰️ Testing NASA API connectivity..." -ForegroundColor Cyan
try {
    docker compose exec -T backend python test_nasa_api.py
    Write-Host "✅ NASA API connection successful" -ForegroundColor Green
} catch {
    Write-Host "⚠️  NASA API test failed, but demo will continue with mock data" -ForegroundColor Yellow
}

# Display access information
Write-Host ""
Write-Host "🎉 FireSight Live Demo is Ready!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Frontend Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔌 API Endpoint:       http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 API Health Check:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "📋 API Documentation:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Demo Features Available:" -ForegroundColor White
Write-Host "   • Real-time wildfire detection simulation" -ForegroundColor Gray
Write-Host "   • Interactive satellite data visualization" -ForegroundColor Gray
Write-Host "   • NASA FIRMS data integration" -ForegroundColor Gray
Write-Host "   • Multi-sensor data fusion" -ForegroundColor Gray
Write-Host "   • Alert system demonstration" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor White
Write-Host "   Stop demo:    docker compose down" -ForegroundColor Gray
Write-Host "   View logs:    docker compose logs -f" -ForegroundColor Gray
Write-Host "   Restart:      docker compose restart" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation: docs/demo-guide.md" -ForegroundColor Cyan
Write-Host ""

# Optional: Open browser automatically
try {
    Write-Host "🚀 Opening demo in browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:3000"
} catch {
    Write-Host "💡 Open http://localhost:3000 in your browser to access the demo" -ForegroundColor Yellow
}

Write-Host "✨ Live demo deployment complete!" -ForegroundColor Green
