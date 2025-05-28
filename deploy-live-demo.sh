#!/usr/bin/env bash
# FireSight AI - Live Demo Deployment Script
# This script sets up a complete live demo environment

set -e

echo "🔥 FireSight AI - Live Demo Deployment"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Setup environment
echo "📋 Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  Please edit .env file with your actual API keys before continuing."
        echo "   Required: NASA_API_KEY"
        read -p "Press Enter after editing .env file..."
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Validate NASA API key
echo "🛰️ Validating NASA API configuration..."
NASA_KEY=$(grep "NASA_API_KEY=" .env | cut -d'=' -f2)
if [ "$NASA_KEY" = "your_nasa_api_key_here" ] || [ -z "$NASA_KEY" ]; then
    echo "❌ Error: Please configure your NASA API key in .env file"
    echo "   Get your free key at: https://firms.modaps.eosdis.nasa.gov/api/area/"
    exit 1
fi
echo "✅ NASA API key configured"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p backend/logs
mkdir -p data
echo "✅ Directories created"

# Build and start services
echo "🐳 Building Docker containers..."
docker compose build --no-cache

echo "🚀 Starting FireSight demo services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API service is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API service failed to start properly"
        docker compose logs api
        exit 1
    fi
    sleep 2
done

# Test NASA API connectivity
echo "🛰️ Testing NASA API connectivity..."
if docker compose exec -T backend python test_nasa_api.py; then
    echo "✅ NASA API connection successful"
else
    echo "⚠️  NASA API test failed, but demo will continue with mock data"
fi

# Display access information
echo ""
echo "🎉 FireSight Live Demo is Ready!"
echo "================================"
echo ""
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "🔌 API Endpoint:       http://localhost:8000"
echo "📊 API Health Check:   http://localhost:8000/health"
echo "📋 API Documentation:  http://localhost:8000/docs"
echo ""
echo "📱 Demo Features Available:"
echo "   • Real-time wildfire detection simulation"
echo "   • Interactive satellite data visualization" 
echo "   • NASA FIRMS data integration"
echo "   • Multi-sensor data fusion"
echo "   • Alert system demonstration"
echo ""
echo "🔧 Management Commands:"
echo "   Stop demo:    docker compose down"
echo "   View logs:    docker compose logs -f"
echo "   Restart:      docker compose restart"
echo ""
echo "📚 Documentation: docs/demo-guide.md"
echo ""

# Optional: Open browser automatically
if command -v xdg-open > /dev/null; then
    echo "🚀 Opening demo in browser..."
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    echo "🚀 Opening demo in browser..."
    open http://localhost:3000
fi

echo "✨ Live demo deployment complete!"
