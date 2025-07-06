# TailorTalk Booking Agent - Setup Script for Windows

Write-Host "🚀 Setting up TailorTalk Booking Agent..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "README.md")) {
    Write-Host "❌ Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install backend dependencies
Write-Host "📚 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install backend dependencies." -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..

# Install frontend dependencies
Write-Host "🎨 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install frontend dependencies." -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..

# Copy environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating environment file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✏️ Please edit .env file with your configuration before running the application." -ForegroundColor Cyan
}

# Check for Google credentials
if (-not (Test-Path "credentials\service-account-key.json")) {
    Write-Host "⚠️ Warning: Google Calendar credentials not found." -ForegroundColor Yellow
    Write-Host "   Please place your service-account-key.json file in the credentials\ folder." -ForegroundColor Yellow
    Write-Host "   See credentials\.gitkeep for instructions." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Edit .env file with your API keys and configuration" -ForegroundColor White
Write-Host "   2. Add Google Calendar credentials to credentials\ folder" -ForegroundColor White
Write-Host "   3. Run: .\start.ps1" -ForegroundColor White
Write-Host ""
