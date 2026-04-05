$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

Write-Host "Starting PathMind backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-Command",
  "Set-Location '$backendDir'; if (Test-Path '.\venv\Scripts\Activate.ps1') { . .\venv\Scripts\Activate.ps1 }; python -m uvicorn main:app --host 0.0.0.0 --port 8000"
)

Start-Sleep -Seconds 3

Write-Host "Starting PathMind frontend on http://localhost:3000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-Command",
  "Set-Location '$frontendDir'; npm.cmd run dev"
)

Start-Sleep -Seconds 5
Start-Process "http://localhost:3000/app.html"

Write-Host ""
Write-Host "PathMind is starting in two new terminals." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000/app.html"
Write-Host "Backend health: http://localhost:8000/health"
