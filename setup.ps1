# FireSight AI Setup Script
# This script sets up the development environment and prepares for deployment

Write-Host "FireSight AI Setup and Deployment" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Yellow

$setupSuccessful = $true

# Function to check if a command exists
function Test-Command($cmdname) {
    try {
        if (Get-Command $cmdname -ErrorAction Stop) { return $true }
    }
    catch { return $false }
}

# Check prerequisites
Write-Host ""
Write-Host "[PREREQUISITES] Checking system requirements..." -ForegroundColor Cyan

# Check Python
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "   [OK] Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Python not found. Please install Python 3.8+" -ForegroundColor Red
    $setupSuccessful = $false
}

# Check Git
if (Test-Command "git") {
    $gitVersion = git --version
    Write-Host "   [OK] Git: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Git not found. Please install Git" -ForegroundColor Red
    $setupSuccessful = $false
}

# Check Docker
if (Test-Command "docker") {
    $dockerVersion = docker --version
    Write-Host "   [OK] Docker: $dockerVersion" -ForegroundColor Green
    $dockerAvailable = $true
} else {
    Write-Host "   [WARNING] Docker not found. Will set up local development environment instead" -ForegroundColor Yellow
    $dockerAvailable = $false
}

# Setup environment file
Write-Host ""
Write-Host "[CONFIG] Setting up environment..." -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "   [OK] Created .env from .env.example" -ForegroundColor Green
        Write-Host "   [ACTION] Please edit .env and add your NASA API key" -ForegroundColor Yellow
    } else {
        Write-Host "   [ERROR] .env.example not found" -ForegroundColor Red
        $setupSuccessful = $false
    }
} else {
    Write-Host "   [OK] .env file already exists" -ForegroundColor Green
}

# Setup Python virtual environment
Write-Host ""
Write-Host "[PYTHON] Setting up Python environment..." -ForegroundColor Cyan

if (-not (Test-Path "venv")) {
    try {
        python -m venv venv
        Write-Host "   [OK] Created Python virtual environment" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] Failed to create virtual environment: $_" -ForegroundColor Red
        $setupSuccessful = $false
    }
} else {
    Write-Host "   [OK] Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
if (Test-Path "venv") {
    Write-Host "   [INFO] Activating virtual environment..." -ForegroundColor Cyan
    
    # Install backend dependencies
    if (Test-Path "backend/requirements.txt") {
        try {
            & "./venv/Scripts/Activate.ps1"
            pip install -r backend/requirements.txt
            Write-Host "   [OK] Installed backend dependencies" -ForegroundColor Green
        } catch {
            Write-Host "   [ERROR] Failed to install backend dependencies: $_" -ForegroundColor Red
            $setupSuccessful = $false
        }
    }
    
    # Install API dependencies
    if (Test-Path "api/requirements.txt") {
        try {
            pip install -r api/requirements.txt
            Write-Host "   [OK] Installed API dependencies" -ForegroundColor Green
        } catch {
            Write-Host "   [ERROR] Failed to install API dependencies: $_" -ForegroundColor Red
            $setupSuccessful = $false
        }
    }
}

# Run tests
Write-Host ""
Write-Host "[TESTING] Running tests..." -ForegroundColor Cyan

if (Test-Path "backend/test_satellite_integration.py") {
    try {
        & "./venv/Scripts/Activate.ps1"
        python -m pytest backend/test_satellite_integration.py -v
        Write-Host "   [OK] Tests passed" -ForegroundColor Green
    } catch {
        Write-Host "   [WARNING] Some tests failed, but continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "   [WARNING] No tests found" -ForegroundColor Yellow
}

# Setup complete
Write-Host ""
if ($setupSuccessful) {
    Write-Host "[SUCCESS] Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[NEXT STEPS]" -ForegroundColor Cyan
    
    if ($dockerAvailable) {
        Write-Host "   Docker Deployment:" -ForegroundColor White
        Write-Host "   1. Edit .env file with your API keys" -ForegroundColor White
        Write-Host "   2. Run: docker-compose up -d" -ForegroundColor White
        Write-Host "   3. Access: http://localhost:3000" -ForegroundColor White
    } else {
        Write-Host "   Local Development:" -ForegroundColor White
        Write-Host "   1. Install Docker Desktop from https://docker.com" -ForegroundColor White
        Write-Host "   2. Edit .env file with your API keys" -ForegroundColor White
        Write-Host "   3. Run: ./venv/Scripts/Activate.ps1" -ForegroundColor White
        Write-Host "   4. Run: python backend/satellite_coordinator.py" -ForegroundColor White
        Write-Host "   5. In another terminal: python api/app.py" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "[API KEYS]" -ForegroundColor Cyan
    Write-Host "   NASA FIRMS API: https://firms.modaps.eosdis.nasa.gov/api/area/" -ForegroundColor White
    Write-Host "   OpenWeatherMap: https://openweathermap.org/api" -ForegroundColor White
    
} else {
    Write-Host "[FAILED] Setup encountered errors. Please fix the issues above." -ForegroundColor Red
}

Write-Host ""
Write-Host "[HELP] For more information:" -ForegroundColor Cyan
Write-Host "   - Documentation: ./docs/" -ForegroundColor White
Write-Host "   - Deployment guide: ./docs/deployment-guide.md" -ForegroundColor White
Write-Host "   - GitHub repo: https://github.com/Rsplitstone/firesight-prototype" -ForegroundColor White
