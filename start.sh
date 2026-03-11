#!/bin/bash

# Proteus launcher — starts both backend and frontend
# Usage: ./start.sh [backend_port]
# Example: ./start.sh 9000

PORT=${1:-8000}

echo ""
echo "  ╔═══════════════════════════════════════╗"
echo "  ║           PROTEUS LAUNCHER            ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""
echo "  Backend port: $PORT"
echo ""

# Check if the port is already in use
if lsof -i :"$PORT" >/dev/null 2>&1; then
  echo "  ⚠ Port $PORT is already in use."
  echo "  Run with a different port: ./start.sh 9000"
  echo ""
  exit 1
fi

# Install backend dependencies if needed
echo "  [1/3] Checking backend dependencies..."
cd "$(dirname "$0")/backend"
pip install -q -r requirements.txt 2>/dev/null

# Install frontend dependencies if needed
echo "  [2/3] Checking frontend dependencies..."
cd "$(dirname "$0")/frontend"
npm install --silent 2>/dev/null

# Start backend
echo "  [3/3] Starting servers..."
echo ""
cd "$(dirname "$0")/backend"
uvicorn main:app --reload --port "$PORT" &
BACKEND_PID=$!

# Start frontend with the API URL pointing to the chosen port
cd "$(dirname "$0")/frontend"
VITE_API_URL="http://localhost:$PORT" npm run dev &
FRONTEND_PID=$!

echo ""
echo "  ✓ Backend:  http://localhost:$PORT"
echo "  ✓ Frontend: http://localhost:3000"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo ""

# Clean up both processes on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
