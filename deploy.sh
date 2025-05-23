#!/bin/bash

# FireSight Deployment Script
# This script helps deploy the FireSight AI platform

set -e

echo "🔥 FireSight AI Deployment Script"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/logs
mkdir -p backend/logs

# Pull latest changes (if this is a git repository)
if [ -d .git ]; then
    echo "📥 Pulling latest changes..."
    git pull origin main
fi

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

echo "🚀 Starting FireSight services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Show logs
echo ""
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "✅ FireSight deployment completed!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo ""
echo "📊 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Update: git pull && docker-compose build && docker-compose up -d"
echo ""
echo "⚙️  Configuration:"
echo "   Edit .env file to customize settings"
echo "   Add your NASA API key for satellite data access"
