# AI Textile Waste Management Platform - Frontend Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting AI Textile Waste Management Platform - Frontend" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$FrontendDir = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path $FrontendDir)) {
    Write-Host "[ERROR] Could not find frontend directory at $FrontendDir" -ForegroundColor Red
    exit 1
}

Set-Location $FrontendDir

$NodeModules = Join-Path $FrontendDir "node_modules"
if (-not (Test-Path $NodeModules)) {
    Write-Host "[INFO] node_modules not detected. Installing dependencies via npm install..." -ForegroundColor Yellow
    npm install
}

Write-Host "[INFO] Starting Vite development server on http://localhost:5173..." -ForegroundColor Green
Write-Host "[INFO] Proxy configured: /api -> http://127.0.0.1:8000" -ForegroundColor Green
npm run dev
