#!/usr/bin/env bash
# Launch Streamlit Enterprise Dashboard
PYTHONPATH=. ./venv/bin/streamlit run frontend_streamlit/app.py --server.port 8501
