#!/bin/sh
set -e

echo "=== Code Analysis Engine — Entrypoint ==="

# Download model from GCS if GCS_MODEL_URI is set
if [ -n "$GCS_MODEL_URI" ]; then
  echo "GCS_MODEL_URI is set — running model download..."
  python download_model.py
else
  echo "GCS_MODEL_URI is not set — skipping model download."
fi

echo "Starting uvicorn server on port ${PORT:-8002}..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8002}"
