#!/usr/bin/env bash
# =============================================================================
# Nexar — Development Server Launcher
#
# Starts all 6 microservices with color-coded logs, hot-reload, and clean
# shutdown. Assumes dependencies are already installed (run setup-dev.sh first).
#
# Usage:
#   bash start-dev.sh                     # Start all services
#   bash start-dev.sh api frontend        # Start only specific services
#   bash start-dev.sh --no-python         # Start only Node services
#   bash start-dev.sh --no-node           # Start only Python services
# =============================================================================

set -uo pipefail
# Enable monitor mode so each background pipeline gets its own process group.
# Without this, signals sent by uvicorn --reload (SIGTERM to its worker) propagate
# up to this bash process on MINGW/Windows and kill all services prematurely.
set -m

# ── Project root ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors (ANSI escape codes) ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'

# Sed-compatible color codes (no \033, use literal escape)
ESC=$'\033'
SED_RED="${ESC}[0;31m"
SED_GREEN="${ESC}[0;32m"
SED_YELLOW="${ESC}[1;33m"
SED_BLUE="${ESC}[0;34m"
SED_MAGENTA="${ESC}[0;35m"
SED_CYAN="${ESC}[0;36m"
SED_WHITE="${ESC}[1;37m"
SED_NC="${ESC}[0m"

# ── OS Detection ──
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    VENV_BIN="Scripts"
    # Force Python to use UTF-8 on Windows (avoids cp1252 UnicodeEncodeError on emoji/unicode)
    export PYTHONUTF8=1
else
    VENV_BIN="bin"
fi

# ── PID Tracking ──
PIDS=()
PID_FILE="$SCRIPT_DIR/.nexar-pids"

# ── CLI Args ──
SKIP_PYTHON=false
SKIP_NODE=false
FORCE_MODELS=false
SELECTED_SERVICES=()

for arg in "$@"; do
    case "$arg" in
        --no-python)     SKIP_PYTHON=true ;;
        --no-node)       SKIP_NODE=true ;;
        --force-models)  FORCE_MODELS=true ;;
        --help|-h)
            echo "Usage: bash start-dev.sh [options] [service ...]"
            echo ""
            echo "Services: frontend api ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer"
            echo ""
            echo "Options:"
            echo "  --no-python      Skip all Python services"
            echo "  --no-node        Skip all Node.js services"
            echo "  --force-models   Re-download all ML models from GCS even if they exist locally"
            echo "  --help, -h       Show this help"
            exit 0
            ;;
        *) SELECTED_SERVICES+=("$arg") ;;
    esac
done

# ── Should we start this service? ──
should_start() {
    local name=$1 type=$2

    # Check type filter
    if [[ "$type" == "python" && "$SKIP_PYTHON" == true ]]; then return 1; fi
    if [[ "$type" == "node" && "$SKIP_NODE" == true ]]; then return 1; fi

    # Check specific service selection
    if [[ ${#SELECTED_SERVICES[@]} -gt 0 ]]; then
        for s in "${SELECTED_SERVICES[@]}"; do
            if [[ "$s" == "$name" ]]; then return 0; fi
        done
        return 1
    fi

    return 0
}

# ── Cleanup on exit ──
cleanup() {
    echo ""
    echo -e "${BOLD}${RED}Shutting down all services...${NC}"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    # Kill any remaining children
    if [[ ${#PIDS[@]} -gt 0 ]]; then
        sleep 1
        for pid in "${PIDS[@]}"; do
            kill -9 "$pid" 2>/dev/null || true
        done
    fi
    rm -f "$PID_FILE"
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# ── GCS Model Configuration ──
# Bucket name and default paths from terraform/variables.tf
GCS_MODELS_BUCKET="${GCS_MODELS_BUCKET:-nexar_models}"

# Default GCS paths per service (can be overridden via env vars)
GCS_PATH_AI_CONVERTER="${GCS_PATH_AI_CONVERTER:-ai-code-converter/version3}"
GCS_PATH_CODE_ANALYSIS="${GCS_PATH_CODE_ANALYSIS:-code-analysis-engine/version2}"

# ── Model download helper ──
# Runs download_model.py for services that need ML models from GCS.
# Checks if models already exist locally before attempting download.
# Uses the service's own venv Python and respects existing .env settings.
maybe_download_models() {
    local name=$1 venv_python=$2 sed_color=$3 label=$4 port=$5

    # Source the service's .env file if present (picks up MODEL_PATH, ML_MODELS_DIR, etc.)
    if [[ -f ".env" ]]; then
        set -a
        source .env
        set +a
    fi

    case "$name" in
        code-analysis-engine)
            local models_dir="${ML_MODELS_DIR:-models/trained}"
            local gcs_uri="${GCS_MODEL_URI:-gs://${GCS_MODELS_BUCKET}/${GCS_PATH_CODE_ANALYSIS}}"

            if [[ "$FORCE_MODELS" == true ]]; then
                echo "Force-downloading models (--force-models)..."
                rm -rf "$models_dir/trained_codebert" "$models_dir/language_classifier" "$models_dir/.deps-installed" 2>/dev/null || true
                # Remove the .pkl skip marker so download_model.py doesn't short-circuit
                rm -f "$models_dir"/*.pkl 2>/dev/null || true
            elif [[ -d "$models_dir/trained_codebert" && -d "$models_dir/language_classifier" ]]; then
                echo "Models already present — skipping GCS download."
                return 0
            fi

            echo "Downloading models from ${gcs_uri} ..."
            GCS_MODEL_URI="$gcs_uri" ML_MODELS_DIR="$models_dir" \
                "$venv_python" download_model.py 2>&1 || {
                echo "WARNING: Model download failed (service will use fallback heuristics)"
            }
            ;;

        ai-code-converter)
            local model_path="${MODEL_PATH:-version3}"
            local gcs_uri="${GCS_MODEL_URI:-gs://${GCS_MODELS_BUCKET}/${GCS_PATH_AI_CONVERTER}}"

            if [[ "$FORCE_MODELS" == true ]]; then
                echo "Force-downloading models (--force-models)..."
                rm -rf "$model_path" 2>/dev/null || true
            elif [[ -f "$model_path/config.json" ]]; then
                echo "Model already present at $model_path — skipping GCS download."
                return 0
            fi

            echo "Downloading models from ${gcs_uri} ..."
            GCS_MODEL_URI="$gcs_uri" MODEL_PATH="$model_path" \
                "$venv_python" download_model.py 2>&1 || {
                echo "WARNING: Model download failed (code conversion will be unavailable)"
            }
            ;;

        *)
            # Other services don't need model downloads
            return 0
            ;;
    esac
}

# ── Service launchers ──

start_python_service() {
    local name=$1 dir=$2 entry=$3 port=$4 color=$5 sed_color=$6 label=$7

    local uvicorn="$SCRIPT_DIR/$dir/.venv/$VENV_BIN/uvicorn"
    local venv_python="$SCRIPT_DIR/$dir/.venv/$VENV_BIN/python"

    if [[ ! -f "$uvicorn" ]]; then
        echo -e "  ${RED}[${label}]${NC} uvicorn not found at $uvicorn — run setup-dev.sh first"
        return
    fi

    echo -e "  ${color}[${label}]${NC} Starting on port ${port} with --reload..."

    (
        cd "$SCRIPT_DIR/$dir"

        # Download models from GCS if needed (ai-code-converter & code-analysis-engine)
        if [[ -f "download_model.py" ]]; then
            maybe_download_models "$name" "$venv_python" "$sed_color" "$label" "$port"
        fi

        "$uvicorn" "$entry" --port "$port" --reload --host 0.0.0.0 2>&1
    ) | sed -u "s/^/${sed_color}[${label}:${port}]${SED_NC} /" &

    PIDS+=($!)
}

start_node_service() {
    local name=$1 dir=$2 port=$3 color=$4 sed_color=$5 label=$6

    if [[ ! -d "$SCRIPT_DIR/$dir/node_modules" ]]; then
        echo -e "  ${RED}[${label}]${NC} node_modules not found — run setup-dev.sh first"
        return
    fi

    echo -e "  ${color}[${label}]${NC} Starting on port ${port}..."

    (
        cd "$SCRIPT_DIR/$dir"
        npm run dev 2>&1
    ) | sed -u "s/^/${sed_color}[${label}:${port}]${SED_NC} /" &

    PIDS+=($!)
}

# =============================================================================
#  MAIN
# =============================================================================

echo ""
echo -e "${BOLD}${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${WHITE}  Nexar — Development Server Launcher${NC}"
echo -e "${BOLD}${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${GRAY}Project root: $SCRIPT_DIR${NC}"
echo -e "  ${GRAY}OS:           $OSTYPE${NC}"
echo ""

# ── Start Python Services ──

if should_start "code-analysis-engine" "python"; then
    start_python_service \
        "code-analysis-engine" \
        "code-analysis-engine" \
        "main:app" \
        8002 \
        "$MAGENTA" "$SED_MAGENTA" "CODE-ANALYSIS"
fi

if should_start "decision-engine" "python"; then
    start_python_service \
        "decision-engine" \
        "decision-engine" \
        "main:app" \
        8003 \
        "$BLUE" "$SED_BLUE" "DECISION-ENGINE"
fi

if should_start "ai-code-converter" "python"; then
    start_python_service \
        "ai-code-converter" \
        "ai-code-converter" \
        "main:app" \
        8001 \
        "$YELLOW" "$SED_YELLOW" "AI-CONVERTER"
fi

if should_start "hardware-abstraction-layer" "python"; then
    start_python_service \
        "hardware-abstraction-layer" \
        "hardware-abstraction-layer" \
        "app.main:app" \
        8004 \
        "$WHITE" "$SED_WHITE" "HAL"
fi

# ── Start Node Services ──

if should_start "api" "node"; then
    start_node_service \
        "api" \
        "api" \
        3000 \
        "$GREEN" "$SED_GREEN" "API"
fi

if should_start "frontend" "node"; then
    start_node_service \
        "frontend" \
        "frontend" \
        5173 \
        "$CYAN" "$SED_CYAN" "FRONTEND"
fi

# ── Save PIDs ──

if [[ ${#PIDS[@]} -eq 0 ]]; then
    echo -e "  ${RED}No services were started.${NC}"
    exit 1
fi

printf "%s\n" "${PIDS[@]}" > "$PID_FILE"

echo ""
echo -e "${BOLD}${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${GREEN}${BOLD}${#PIDS[@]} services started.${NC} Press ${BOLD}Ctrl+C${NC} to stop all."
echo ""
echo -e "  ${MAGENTA}[CODE-ANALYSIS]${NC}   http://localhost:8002"
echo -e "  ${BLUE}[DECISION-ENGINE]${NC} http://localhost:8003"
echo -e "  ${YELLOW}[AI-CONVERTER]${NC}    http://localhost:8001"
echo -e "  ${WHITE}[HAL]${NC}             http://localhost:8004"
echo -e "  ${GREEN}[API]${NC}             http://localhost:3000"
echo -e "  ${CYAN}[FRONTEND]${NC}        http://localhost:5173"
echo -e "${BOLD}${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── Wait for all processes ──
wait "${PIDS[@]}" 2>/dev/null || true
