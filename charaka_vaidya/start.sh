#!/bin/bash
set -e

echo "🚀 Starting Charaka Vaidya..."

# Start FastAPI backend in background
echo "  → Starting FastAPI on port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend in foreground
echo "  → Starting Streamlit on port 8501..."
streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
