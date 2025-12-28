@echo off
REM Script to run the FastAPI backend on Windows

echo Starting GenAI Document Assistant API...
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
