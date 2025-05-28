# FireSight Live Demo - Quick Validation
# Run this script to validate your demo deployment

Write-Host "🔥 FireSight AI - Live Demo Validation" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Yellow

$errors = 0

# Test if Docker is running
Write-Host "🐳 Checking Docker..." -ForegroundColor Cyan
try {
    docker version | Out-Null
    Write-Host "   ✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker is not running or not installed" -ForegroundColor Red
    $errors++
}

# Test if services are running
Write-Host "🔧 Checking services..." -ForegroundColor Cyan

$services = @(
    @{name="API"; url="http://localhost:8000/health"; port=8000},
    @{name="Frontend"; url="http://localhost:3000"; port=3000}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($service.name) is running (Port $($service.port))" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $($service.name) returned status $($response.StatusCode)" -ForegroundColor Red
            $errors++
        }
    } catch {
        Write-Host "   ❌ $($service.name) is not responding (Port $($service.port))" -ForegroundColor Red
        $errors++
    }
}

# Test demo endpoints
Write-Host "🎮 Testing demo endpoints..." -ForegroundColor Cyan

$demoEndpoints = @(
    "http://localhost:8000/demo/status",
    "http://localhost:8000/demo/metrics"
)

foreach ($endpoint in $demoEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $(Split-Path $endpoint -Leaf) endpoint working" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $(Split-Path $endpoint -Leaf) endpoint failed" -ForegroundColor Red
            $errors++
        }
    } catch {
        Write-Host "   ❌ $(Split-Path $endpoint -Leaf) endpoint not responding" -ForegroundColor Red
        $errors++
    }
}

# Check environment configuration
Write-Host "⚙️ Checking configuration..." -ForegroundColor Cyan

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "NASA_API_KEY=([^`r`n]+)") {
        $apiKey = $matches[1]
        if ($apiKey -and $apiKey -ne "your_nasa_api_key_here") {
            Write-Host "   ✅ NASA API key configured" -ForegroundColor Green
        } else {
            Write-Host "   ❌ NASA API key not configured" -ForegroundColor Red
            $errors++
        }
    } else {
        Write-Host "   ❌ NASA API key not found in .env" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "   ❌ .env file not found" -ForegroundColor Red
    $errors++
}

# Summary
Write-Host ""
if ($errors -eq 0) {
    Write-Host "🎉 Live Demo Validation PASSED!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Your live demo is ready!" -ForegroundColor Cyan
    Write-Host "   Dashboard: http://localhost:3000" -ForegroundColor White
    Write-Host "   API:       http://localhost:8000" -ForegroundColor White
    Write-Host "   Docs:      http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Ready to present FireSight AI!" -ForegroundColor Yellow
    
    # Optionally open browser
    try {
        Start-Process "http://localhost:3000"
        Write-Host "🌐 Opening dashboard in browser..." -ForegroundColor Cyan
    } catch {
        Write-Host "💡 Open http://localhost:3000 in your browser" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Live Demo Validation FAILED!" -ForegroundColor Red
    Write-Host "===============================" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 $errors error(s) found. Please fix and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Common fixes:" -ForegroundColor Cyan
    Write-Host "   - Run: .\deploy-live-demo.ps1" -ForegroundColor White
    Write-Host "   - Check: docker compose logs" -ForegroundColor White
    Write-Host "   - Restart: docker compose restart" -ForegroundColor White
}
