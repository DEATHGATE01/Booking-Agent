# TailorTalk Booking Agent - Simple Setup Script

Write-Host "Setting up TailorTalk Booking Agent..." -ForegroundColor Green

# Check if Python is installed
$pythonCheck = python --version 2>$null
if (-not $pythonCheck) {
    Write-Host "Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

Write-Host "Python found: $pythonCheck" -ForegroundColor Green

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install backend dependencies
Set-Location backend
pip install -r requirements.txt
Set-Location ..

# Install frontend dependencies  
Set-Location frontend
pip install -r requirements.txt
Set-Location ..

# Create .env file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file. Please edit it with your API keys." -ForegroundColor Cyan
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "2. Add Google credentials to credentials folder" -ForegroundColor White
Write-Host "3. Run start.ps1 to start the application" -ForegroundColor White
