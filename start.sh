#!/bin/bash

# CodeGraph Quick Start Script (macOS/Linux)
echo "🕸️  CodeGraph Quick Start"
echo "=========================="
echo ""

# Get absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Helper for errors
error_exit() {
    echo "❌ ERROR: $1"
    exit 1
}

# 1. Check for Git
if ! command -v git &> /dev/null; then
    error_exit "Git is not installed. Please install it first."
fi
echo "✅ Git found"

# 2. Check for Python 3.10+
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 is not installed."
fi

python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"
if [ $? -ne 0 ]; then
    error_exit "Python 3.10+ is required. Current: $(python3 --version)"
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2) found"

# 3. Check for Node.js 18+
if ! command -v node &> /dev/null; then
    error_exit "Node.js is not installed."
fi

node -e "const v = process.version.slice(1).split('.')[0]; process.exit(v >= 18 ? 0 : 1)"
if [ $? -ne 0 ]; then
    error_exit "Node.js 18+ is required. Current: $(node --version)"
fi
echo "✅ Node.js $(node --version) found"

# 4. Check for Port Conflicts
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    error_exit "Port 8000 is already in use (Backend target). Please free it and try again."
fi
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    error_exit "Port 3000 is already in use (Frontend target). Please free it and try again."
fi
echo "✅ Ports 8000/3000 are available"
echo ""

# --- Setup Backend ---
echo "📦 Setting up backend..."
cd "$SCRIPT_DIR/backend" || error_exit "Backend directory not found"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || error_exit "Failed to create virtual environment"
fi

source venv/bin/activate || error_exit "Failed to activate virtual environment"
echo "Installing/Updating Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt || error_exit "Failed to install backend dependencies"

echo "✅ Backend setup complete!"
echo ""

# --- Setup Frontend ---
echo "📦 Setting up frontend..."
cd "$SCRIPT_DIR/frontend" || error_exit "Frontend directory not found"

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies (this may take a minute)..."
    npm install || error_exit "npm install failed"
fi

echo "✅ Frontend setup complete!"
echo ""

# --- Launching ---
echo "🚀 Starting CodeGraph..."
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping CodeGraph..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

# Start backend in background
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Small delay to let backend start
sleep 2

# Start frontend
cd "$SCRIPT_DIR/frontend"
npm start &
FRONTEND_PID=$!

# Wait for background processes
wait
