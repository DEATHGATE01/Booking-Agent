# TailorTalk Booking Agent - Start Script for Windows

Write-Host "🚀 Starting TailorTalk Booking Agent..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

Write-Host "🔧 Starting FastAPI backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\activate.ps1; cd backend; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "🎨 Starting Streamlit frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\activate.ps1; cd frontend; streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"

Write-Host ""
Write-Host "🌟 TailorTalk Booking Agent is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend (Streamlit): http://localhost:8501" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both services are starting in separate windows..." -ForegroundColor Yellow
Write-Host "Press any key to exit this script..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
