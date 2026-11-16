# AI Textile Waste Management Platform - Backend Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting AI Textile Waste Management Platform - Backend " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$BackendDir = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $BackendDir)) {
    Write-Host "[ERROR] Could not find backend directory at $BackendDir" -ForegroundColor Red
    exit 1
}

Set-Location $BackendDir

# Use virtual environment python if available
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
    Write-Host "[INFO] Using virtual environment Python at $VenvPython" -ForegroundColor Green
} else {
    $PythonExe = "python"
    Write-Host "[INFO] Using system Python" -ForegroundColor Yellow
}

# Run Database Migrations
Write-Host "[INFO] Running database schema migrations (Alembic)..." -ForegroundColor Yellow
& $PythonExe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Alembic migration reported an exit code of $LASTEXITCODE. Continuing startup..." -ForegroundColor DarkYellow
}

# Ensure Initial Administrator Account Exists
Write-Host "[INFO] Bootstrapping initial administrator account..." -ForegroundColor Yellow
& $PythonExe scripts/create_initial_admin.py

# Start Uvicorn Server
Write-Host "[INFO] Starting FastAPI server on http://127.0.0.1:8000..." -ForegroundColor Green
Write-Host "[INFO] API Docs available at: http://127.0.0.1:8000/docs" -ForegroundColor Green
& $PythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
