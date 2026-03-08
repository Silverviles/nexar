#!/bin/sh
set -e

echo "=== Code Analysis Engine — Entrypoint ==="
echo "Python version: $(python --version 2>&1)"
echo "PORT=${PORT:-8002}"
echo "ML_MODELS_DIR=${ML_MODELS_DIR:-models/trained}"
echo "GCS_MODEL_URI=${GCS_MODEL_URI:-<not set>}"

# Download model from GCS if GCS_MODEL_URI is set
if [ -n "$GCS_MODEL_URI" ]; then
  echo "GCS_MODEL_URI is set — running model download..."
  python download_model.py
else
  echo "GCS_MODEL_URI is not set — skipping model download."
fi

echo "Starting uvicorn server on port ${PORT:-8002}..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8002}"
