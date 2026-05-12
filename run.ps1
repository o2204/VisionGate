# VisionGate Run Script for Windows (PowerShell)

# Kill existing processes on port 8000
Write-Host "Cleaning up existing processes on port 8000..." -ForegroundColor Yellow

$ports = @(8000)

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

    foreach ($conn in $connections) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

# Root directory
$RootPath = Get-Location

# =========================
# Backend
# =========================
Write-Host "Starting Backend API..." -ForegroundColor Cyan

$BackendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    
    # Check if venv exists, create if not
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv venv
    }
    
    # Activate venv and install/run
    & ".\venv\Scripts\Activate.ps1"
    
    # Simple check for dependencies
    try {
        python -c "import fastapi"
    } catch {
        Write-Host "Installing backend dependencies..."
        pip install -r requirements.txt
    }

    Write-Host "Starting FastAPI Backend on http://localhost:8000"
    uvicorn src.main:app --reload --port 8000
} -ArgumentList (Join-Path $RootPath "backend")

# =========================
# Frontend
# =========================
Write-Host "Starting Flutter Frontend..." -ForegroundColor Cyan

$FrontendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path

    Write-Host "Getting Flutter packages..."
    flutter pub get

    Write-Host "Starting Flutter app..."
    # Note: Using windows target by default for run.ps1
    flutter run -d windows
} -ArgumentList (Join-Path $RootPath "ui/visiongate")

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "All services are starting!"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: Flutter Windows App"
Write-Host "Note: If you are on Linux, use ./run.sh instead."
Write-Host "Press Ctrl+C to stop everything."
Write-Host "====================================="

# Function to stop all jobs when script exits
function Cleanup {
    Write-Host "`nStopping all services..." -ForegroundColor Red
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    exit
}

# Catch Ctrl+C
$null = Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

try {
    Wait-Job -Job $BackendJob, $FrontendJob
} finally {
    Cleanup
}