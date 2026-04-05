@echo off
title PathMind AI - Launcher
color 0A

echo ============================================
echo    PathMind AI - One-Click Launcher
echo ============================================
echo.

REM Get the directory where this script lives
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

echo [1/3] Starting Backend Server (port 8000)...
start "PathMind Backend" cmd /k "cd /d "%BACKEND%" && call venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo      Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [2/3] Starting Frontend Server (port 3000)...
start "PathMind Frontend" cmd /k "cd /d "%FRONTEND%" && npx next dev"

echo      Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

echo [3/3] Opening website in browser...
start http://localhost:3000/app.html

echo.
echo ============================================
echo    PathMind AI is now running!
echo ============================================
echo.
echo    Frontend:  http://localhost:3000/app.html
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/api/docs
echo    Health:    http://localhost:8000/health
echo.
echo    To stop: Close the Backend and Frontend
echo    terminal windows, or run STOP-PATHMIND.bat
echo ============================================
echo.
pause
