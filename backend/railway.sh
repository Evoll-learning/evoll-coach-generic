#!/bin/bash
# Railway startup script for backend

echo "🚀 Starting EvoLL Backend on Railway..."

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
