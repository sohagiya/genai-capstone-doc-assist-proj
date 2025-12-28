#!/bin/bash
# Script to run the FastAPI backend

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the API server
echo "Starting GenAI Document Assistant API..."
python -m uvicorn backend.app.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000} --reload
