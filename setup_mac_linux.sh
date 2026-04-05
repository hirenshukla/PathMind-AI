#!/bin/bash
# PathMind AI — Mac/Linux Auto Setup & Run Script
# Usage: chmod +x setup_mac_linux.sh && ./setup_mac_linux.sh

set -e

echo ""
echo "========================================"
echo "  PathMind AI — Setup (Mac/Linux)"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} $1 found: $($1 --version 2>&1 | head -1)"
    else
        echo -e "${RED}[MISSING]${NC} $1 not found"
        echo "Install from: $2"
        exit 1
    fi
}

# Check dependencies
echo "--- Checking dependencies ---"
check_command python3 "https://python.org/downloads"
check_command node "https://nodejs.org"
check_command psql "https://postgresql.org/download"

# ── BACKEND SETUP ──────────────────────────────────────
echo ""
echo "--- Setting up Backend ---"
cd backend

# Virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python packages (3-5 minutes)..."
pip install -r requirements.txt -q

echo "Installing spaCy language model..."
python -m spacy download en_core_web_sm

# Create .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}Created .env — please edit DATABASE_URL before running${NC}"
fi

cd ..

# ── FRONTEND SETUP ─────────────────────────────────────
echo ""
echo "--- Setting up Frontend ---"
cd frontend

echo "Installing Node.js packages (2-3 minutes)..."
npm install --silent

# Create .env.local
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
    echo "Created .env.local"
fi

cd ..

# ── DONE ───────────────────────────────────────────────
echo ""
echo -e "${GREEN}========================================"
echo "  Setup Complete!"
echo -e "========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure PostgreSQL is running:"
echo "   Mac:   brew services start postgresql"
echo "   Linux: sudo systemctl start postgresql"
echo ""
echo "2. Create database (if not done):"
echo "   sudo -u postgres psql"
echo "   CREATE DATABASE pathmind_db;"
echo "   CREATE USER pathmind_user WITH PASSWORD 'pathmind123';"
echo "   GRANT ALL PRIVILEGES ON DATABASE pathmind_db TO pathmind_user;"
echo "   \q"
echo ""
echo "3. Edit backend/.env — set DATABASE_URL"
echo ""
echo "4. Run database setup:"
echo "   python database/setup.py"
echo ""
echo "5. Start both servers:"
echo "   ./run_all.sh"
echo ""
