#!/bin/bash

# Install frontend dependencies
cd apps/web
pnpm install
cd ../..

# Create and activate Python virtual environment
cd backend
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Installation complete. To start the application, run: pnpm dev"
