#!/usr/bin/env bash
# Launch FastAPI Enterprise Backend Server with Live Reload
echo "🚀 Starting Enterprise Multi-Agent Backend Server on port 8010..."
PYTHONPATH=. ./venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8010 --reload
