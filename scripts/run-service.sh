#!/usr/bin/env bash
# Starts a single backend service in the foreground, then drops into an
# interactive shell so the terminal window stays open after Ctrl+C or a crash.
# Called by the root Makefile — one instance per service, each in its own
# terminal window (see `make backend`).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

SERVICE="${1:?Usage: run-service.sh <service-name>}"

case "$SERVICE" in
    ai-code-converter)
        cd ai-code-converter && .venv/Scripts/uvicorn main:app --port 8001 --reload --host 0.0.0.0
        ;;
    code-analysis-engine)
        cd code-analysis-engine && .venv/Scripts/uvicorn main:app --port 8002 --reload --host 0.0.0.0
        ;;
    decision-engine)
        cd decision-engine && .venv/Scripts/uvicorn main:app --port 8003 --reload --host 0.0.0.0
        ;;
    hardware-abstraction-layer)
        cd hardware-abstraction-layer && .venv/Scripts/uvicorn app.main:app --port 8004 --reload --host 0.0.0.0
        ;;
    api)
        cd api && npm run dev
        ;;
    *)
        echo "Unknown service: $SERVICE"
        exit 1
        ;;
esac

echo ""
echo "[$SERVICE] exited. Dropping into shell (Ctrl+D to close window)."
exec bash
