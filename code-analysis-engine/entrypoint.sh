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

# Test critical imports before starting the server so that any
# ImportError / dependency conflict shows up clearly in logs
# instead of a generic "container failed to listen on PORT" message.
echo ""
echo "=== Testing critical imports ==="
python -c "
import sys
errors = []

modules = [
    ('fastapi', 'fastapi'),
    ('uvicorn', 'uvicorn'),
    ('pydantic', 'pydantic'),
    ('numpy', 'numpy'),
    ('joblib', 'joblib'),
    ('sklearn', 'scikit-learn'),
    ('networkx', 'networkx'),
    ('matplotlib', 'matplotlib'),
    ('tree_sitter', 'tree-sitter'),
    ('qiskit', 'qiskit'),
    ('cirq', 'cirq'),
    ('pennylane', 'pennylane'),
    ('google.cloud.storage', 'google-cloud-storage'),
    ('google.cloud.logging', 'google-cloud-logging'),
]

for mod, pkg in modules:
    try:
        __import__(mod)
        print(f'  ✅ {mod}')
    except Exception as e:
        print(f'  ❌ {mod} ({pkg}): {e}')
        errors.append((mod, str(e)))

if errors:
    print()
    print(f'⚠️  {len(errors)} import(s) failed — server may crash at startup.')
    for mod, err in errors:
        print(f'   • {mod}: {err}')
else:
    print('  All critical imports OK.')
"
echo ""

# Test that the app module itself can be imported
echo "=== Testing app import (main:app) ==="
python -c "
try:
    from main import app
    print('  ✅ main:app imported successfully')
except Exception as e:
    print(f'  ❌ Failed to import main:app: {e}')
    import traceback
    traceback.print_exc()
" || true
echo ""

echo "Starting uvicorn server on port ${PORT:-8002}..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8002}"
