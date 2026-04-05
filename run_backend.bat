@echo off
REM PathMind AI — Start Backend (Windows)
echo Starting PathMind AI Backend...
cd backend
call venv\Scripts\activate.bat
echo Backend running at: http://localhost:8000
echo API Docs at: http://localhost:8000/api/docs
echo Press Ctrl+C to stop
python -m uvicorn main:app --host 0.0.0.0 --port 8000
