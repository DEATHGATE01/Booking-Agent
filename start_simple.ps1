# Simple Start Script for TailorTalk Booking Agent

Write-Host "Starting TailorTalk Booking Agent..." -ForegroundColor Green

# Check virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Copy .env.example to .env first." -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/c", "cd /d `"$PWD`" && venv\Scripts\activate && cd backend && python -m uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starting frontend..." -ForegroundColor Yellow  
Start-Process cmd -ArgumentList "/c", "cd /d `"$PWD`" && venv\Scripts\activate && cd frontend && streamlit run streamlit_app.py --server.port 8501"

Write-Host ""
Write-Host "Services are starting..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
