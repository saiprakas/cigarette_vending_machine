# Cigarette Vending Machine - Startup Script
# This script starts both the backend and frontend servers automatically

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Cigarette Vending Machine - Starting" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python virtual environment exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "[1/3] Activating Python virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

Write-Host ""

# Start Backend Server in background
Write-Host "[2/3] Starting Backend Server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    param($workingDir)
    Set-Location $workingDir
    & .\.venv\Scripts\Activate.ps1
    Set-Location backend
    python app_simple.py
} -ArgumentList $PWD

Start-Sleep -Seconds 2

# Check if backend started successfully
if ($backendJob.State -eq "Running") {
    Write-Host "✓ Backend server starting on http://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "✗ Backend server failed to start" -ForegroundColor Red
}

Write-Host ""

# Start Frontend Server
Write-Host "[3/3] Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "✓ Frontend will open on http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   Both servers are now running!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Start frontend (this will keep the terminal open)
npm run dev
