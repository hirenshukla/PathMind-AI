@echo off
setlocal enabledelayedexpansion
cd c:\Users\user\Desktop\pathmind-saas\frontend
set PATH=C:\Program Files\nodejs;%PATH%
echo Installing dependencies...
call npm install
echo.
echo Starting frontend development server...
echo Frontend will be available at: http://localhost:3000
echo.
call npm run dev
