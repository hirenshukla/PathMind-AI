#!/bin/bash
# PathMind AI — Start Both Servers (Mac/Linux)
# Usage: chmod +x run_all.sh && ./run_all.sh

echo ""
echo "========================================"
echo "  PathMind AI — Starting Servers"
echo "========================================"
echo ""

# Start backend in background
echo "Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

echo "Backend started! PID: $BACKEND_PID"
echo "  → API: http://localhost:8000"
echo "  → Docs: http://localhost:8000/api/docs"
echo ""

# Start frontend
echo "Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 3

echo ""
echo "========================================"
echo "  Both servers running!"
echo "========================================"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Open browser automatically
sleep 2
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
fi

# Wait and handle Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
