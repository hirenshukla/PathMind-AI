@echo off
REM PathMind AI — Windows Auto Setup Script
REM Double-click this file to set up everything automatically

echo.
echo ========================================
echo   PathMind AI — Auto Setup (Windows)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Setup backend
echo.
echo --- Setting up Backend ---
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python packages (this takes 3-5 minutes)...
pip install -r requirements.txt --quiet

echo Installing spaCy language model...
python -m spacy download en_core_web_sm

REM Create .env if not exists
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit backend\.env file and set your DATABASE_URL
    echo Default: postgresql+asyncpg://postgres:password@localhost:5432/pathmind_db
)

cd ..

REM Setup frontend
echo.
echo --- Setting up Frontend ---
cd frontend

echo Installing Node packages (this takes 2-3 minutes)...
call npm install --quiet

REM Create .env.local
if not exist .env.local (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 > .env.local
    echo Created .env.local
)

cd ..

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Make sure PostgreSQL is running
echo 2. Edit backend\.env - set your database password
echo 3. Run: python database\setup.py
echo 4. Start backend: run_backend.bat
echo 5. Start frontend: run_frontend.bat
echo.
pause
