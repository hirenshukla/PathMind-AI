@echo off
title PathMind AI - Stopping Services
color 0C

echo ============================================
echo    PathMind AI - Stopping All Services
echo ============================================
echo.

echo Stopping backend (uvicorn on port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Stopping frontend (Next.js on port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo All PathMind services stopped.
echo.
pause
