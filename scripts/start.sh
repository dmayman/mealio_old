#!/bin/bash

# Start the Python backend in the background
echo "Starting Python backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
PYTHON_PID=$!
cd ..

# Start the Next.js frontend
echo "Starting Next.js frontend..."
cd apps/web
pnpm dev &
NEXT_PID=$!
cd ../..

# Function to kill both processes when script is terminated
cleanup() {
  echo "Stopping services..."
  kill $PYTHON_PID $NEXT_PID 2>/dev/null
  exit 0
}

# Set up trap to catch termination signals
trap cleanup INT TERM

# Wait for both processes
echo "Services are running. Press Ctrl+C to stop."
wait $PYTHON_PID $NEXT_PID
