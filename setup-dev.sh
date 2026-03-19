#!/usr/bin/env bash
# =============================================================================
# Nexar — Development Environment Setup
#
# Checks prerequisites (Python ≥3.12, Node ≥22), installs them if missing,
# then creates Python venvs and installs all dependencies IN PARALLEL.
#
# Supports: Windows (Git Bash/MSYS), macOS (Homebrew), Ubuntu/Debian (apt)
#
# Usage:
#   bash setup-dev.sh                     # Setup all services
#   bash setup-dev.sh <service-name>      # Setup only one service
#   bash setup-dev.sh --force             # Force reinstall (recreates venvs)
#   bash setup-dev.sh --force <service>   # Force reinstall one service
#   bash setup-dev.sh --skip-prereqs      # Skip prerequisite checks
#   bash setup-dev.sh --help              # Show usage
# =============================================================================

set -uo pipefail

# ── Project root ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ──
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

# ── Minimum versions ──
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=12
MIN_NODE_MAJOR=22

# =============================================================================
#  PHASE 0: OS & Platform Detection
# =============================================================================

detect_platform() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "${OSTYPE:-}" == "win32" ]]; then
        PLATFORM="windows"
        VENV_BIN="Scripts"
        PKG_MGR="winget"
    elif [[ "$(uname -s)" == "Darwin" ]]; then
        PLATFORM="macos"
        VENV_BIN="bin"
        PKG_MGR="brew"
    elif [[ "$(uname -s)" == "Linux" ]]; then
        if [[ -f /etc/os-release ]] && grep -qiE 'ubuntu|debian' /etc/os-release; then
            PLATFORM="ubuntu"
        else
            PLATFORM="linux-other"
        fi
        VENV_BIN="bin"
        PKG_MGR="apt"
    else
        PLATFORM="unknown"
        VENV_BIN="bin"
        PKG_MGR="manual"
    fi
}

# ── CLI Args ──
FORCE=false
SKIP_PREREQS=false
TARGET_SERVICE=""
SHOW_HELP=false

for arg in "$@"; do
    case "$arg" in
        --force)        FORCE=true ;;
        --skip-prereqs) SKIP_PREREQS=true ;;
        --help|-h)      SHOW_HELP=true ;;
        -*)             echo "Unknown flag: $arg"; exit 1 ;;
        *)              TARGET_SERVICE="$arg" ;;
    esac
done

if [[ "$SHOW_HELP" == true ]]; then
    cat <<'USAGE'
Nexar Development Environment Setup

Usage:
  bash setup-dev.sh                     Setup all services
  bash setup-dev.sh <service-name>      Setup only one service
  bash setup-dev.sh --force             Force reinstall (recreates venvs/node_modules)
  bash setup-dev.sh --force <service>   Force reinstall one service
  bash setup-dev.sh --skip-prereqs      Skip Python/Node prerequisite checks
  bash setup-dev.sh --help              Show this help

Service names:
  ai-code-converter         Python  (port 8001)
  code-analysis-engine      Python  (port 8002)
  decision-engine           Python  (port 8003)
  hardware-abstraction-layer Python (port 8004)
  api                       Node.js (port 3000)
  frontend                  Node.js (port 5173)

Examples:
  bash setup-dev.sh --force code-analysis-engine   Recreate broken venv
  bash setup-dev.sh --skip-prereqs                 Skip install checks
USAGE
    exit 0
fi

# ── Logging helpers ──
log_header() {
    echo ""
    echo -e "${BOLD}${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${WHITE}  $1${NC}"
    echo -e "${BOLD}${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_info() {
    echo -e "  ${GRAY}$1${NC}"
}

log_ok() {
    local color=$1 name=$2 msg=$3
    echo -e "  ${color}[${name}]${NC} ${GREEN}✓${NC} ${msg}"
}

log_warn() {
    local color=$1 name=$2 msg=$3
    echo -e "  ${color}[${name}]${NC} ${YELLOW}! ${msg}${NC}"
}

log_fail() {
    local color=$1 name=$2 msg=$3
    echo -e "  ${color}[${name}]${NC} ${RED}✗ ${msg}${NC}"
}

log_step() {
    local color=$1 name=$2 msg=$3
    echo -e "  ${color}[${name}]${NC} ${msg}"
}

log_skip() {
    local color=$1 name=$2 msg=$3
    echo -e "  ${color}[${name}]${NC} ${GRAY}⊘ ${msg} (use --force to reinstall)${NC}"
}

# ── Track results (file-based for subshell compatibility) ──
RESULTS_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'nexar-setup')
set_result() {
    local name=$1 status=$2
    echo "$status" > "$RESULTS_DIR/$name"
}
get_result() {
    local name=$1
    if [[ -f "$RESULTS_DIR/$name" ]]; then
        cat "$RESULTS_DIR/$name"
    else
        echo "UNKNOWN"
    fi
}

# ── Should we set up this service? ──
should_setup() {
    local name=$1
    [[ -z "$TARGET_SERVICE" ]] || [[ "$TARGET_SERVICE" == "$name" ]]
}

# =============================================================================
#  PHASE 1: Prerequisite Checks
# =============================================================================

# Get the best python command for this platform.
# Prefers exact version match (python3.12) over generic (python3/python).
# On Windows, also tries the `py` launcher with version flag.
find_python_cmd() {
    local candidates=()

    if [[ "$PLATFORM" == "windows" ]]; then
        # Windows: try py launcher (most reliable version selection), then versioned, then generic
        candidates=(
            "py -3.${MIN_PYTHON_MINOR}"
            "python${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}"
            "python3.${MIN_PYTHON_MINOR}"
            "python3"
            "python"
        )
    else
        # Unix: try versioned first, then generic
        candidates=(
            "python${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}"
            "python3.${MIN_PYTHON_MINOR}"
            "python3"
            "python"
        )
    fi

    for cmd in "${candidates[@]}"; do
        # For multi-word commands like "py -3.12", test differently
        if [[ "$cmd" == *" "* ]]; then
            if $cmd --version &>/dev/null 2>&1; then
                echo "$cmd"
                return
            fi
        else
            if command -v "$cmd" &>/dev/null; then
                # Verify it's actually the right version
                local ver
                ver=$($cmd --version 2>&1 | head -1 | sed -n 's/.*Python \([0-9]*\)\.\([0-9]*\).*/\1.\2/p')
                local major minor
                major=$(echo "$ver" | cut -d. -f1)
                minor=$(echo "$ver" | cut -d. -f2)
                if [[ -n "$major" && -n "$minor" ]]; then
                    if (( major == MIN_PYTHON_MAJOR && minor == MIN_PYTHON_MINOR )); then
                        echo "$cmd"
                        return
                    fi
                fi
            fi
        fi
    done

    # Fallback: return any python that meets the minimum version
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$($cmd --version 2>&1 | head -1 | sed -n 's/.*Python \([0-9]*\)\.\([0-9]*\).*/\1 \2/p')
            local major minor
            major=$(echo "$ver" | cut -d' ' -f1)
            minor=$(echo "$ver" | cut -d' ' -f2)
            if [[ -n "$major" && -n "$minor" ]]; then
                if version_ge "$major" "$minor" "$MIN_PYTHON_MAJOR" "$MIN_PYTHON_MINOR"; then
                    echo "$cmd"
                    return
                fi
            fi
        fi
    done

    echo ""
}

# Parse version from "Python 3.12.7" or "v22.11.0"
parse_python_version() {
    local version_str
    version_str=$("$1" --version 2>&1 | head -1)
    echo "$version_str" | sed -n 's/.*Python \([0-9]*\)\.\([0-9]*\).*/\1 \2/p'
}

parse_node_version() {
    local version_str
    version_str=$(node --version 2>&1 | head -1)
    echo "$version_str" | sed -n 's/v\([0-9]*\).*/\1/p'
}

# Compare: returns 0 if current >= required
version_ge() {
    local cur_major=$1 cur_minor=$2 req_major=$3 req_minor=$4
    if (( cur_major > req_major )); then return 0; fi
    if (( cur_major == req_major && cur_minor >= req_minor )); then return 0; fi
    return 1
}

install_python() {
    echo -e "  ${YELLOW}Attempting to install Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}...${NC}"
    case "$PLATFORM" in
        ubuntu)
            echo -e "  ${GRAY}Running: sudo apt update && sudo apt install -y python3.12 python3.12-venv python3-pip${NC}"
            sudo apt update -qq && sudo apt install -y python3.12 python3.12-venv python3-pip
            ;;
        macos)
            if ! command -v brew &>/dev/null; then
                echo -e "  ${RED}Homebrew not found. Install it from https://brew.sh then re-run.${NC}"
                return 1
            fi
            echo -e "  ${GRAY}Running: brew install python@3.12${NC}"
            brew install python@3.12
            ;;
        windows)
            echo -e "  ${GRAY}Running: winget install Python.Python.3.12${NC}"
            winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
            # winget installs may need a shell restart to update PATH
            echo -e "  ${YELLOW}If Python is still not found after install, restart your terminal.${NC}"
            ;;
        *)
            echo -e "  ${RED}Cannot auto-install Python on this platform.${NC}"
            echo -e "  ${RED}Please install Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ manually from https://python.org${NC}"
            return 1
            ;;
    esac
}

install_node() {
    echo -e "  ${YELLOW}Attempting to install Node.js ${MIN_NODE_MAJOR}...${NC}"
    case "$PLATFORM" in
        ubuntu)
            echo -e "  ${GRAY}Running: NodeSource setup + apt install nodejs${NC}"
            curl -fsSL "https://deb.nodesource.com/setup_${MIN_NODE_MAJOR}.x" | sudo -E bash -
            sudo apt install -y nodejs
            ;;
        macos)
            if ! command -v brew &>/dev/null; then
                echo -e "  ${RED}Homebrew not found. Install it from https://brew.sh then re-run.${NC}"
                return 1
            fi
            echo -e "  ${GRAY}Running: brew install node@${MIN_NODE_MAJOR}${NC}"
            brew install "node@${MIN_NODE_MAJOR}"
            ;;
        windows)
            echo -e "  ${GRAY}Running: winget install OpenJS.NodeJS.LTS${NC}"
            winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
            echo -e "  ${YELLOW}If Node is still not found after install, restart your terminal.${NC}"
            ;;
        *)
            echo -e "  ${RED}Cannot auto-install Node.js on this platform.${NC}"
            echo -e "  ${RED}Please install Node.js ${MIN_NODE_MAJOR}+ from https://nodejs.org${NC}"
            return 1
            ;;
    esac
}

check_prerequisites() {
    local all_ok=true

    # ── Python ──
    echo ""
    echo -e "  ${BOLD}Checking Python...${NC}"

    # find_python_cmd already validates version >= MIN, so if it returns
    # something, we know it's good.
    PYTHON_CMD=$(find_python_cmd)

    if [[ -n "$PYTHON_CMD" ]]; then
        # Get display version
        local py_ver_str
        py_ver_str=$($PYTHON_CMD --version 2>&1 | head -1)
        log_ok "$GREEN" "PYTHON" "Found: $py_ver_str (command: $PYTHON_CMD)"
    else
        log_fail "$YELLOW" "PYTHON" "Python >= ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR} not found"
        install_python || true
        # Re-check after install
        PYTHON_CMD=$(find_python_cmd)
        if [[ -n "$PYTHON_CMD" ]]; then
            local py_ver_str
            py_ver_str=$($PYTHON_CMD --version 2>&1 | head -1)
            log_ok "$GREEN" "PYTHON" "Installed: $py_ver_str (command: $PYTHON_CMD)"
        else
            log_fail "$RED" "PYTHON" "Python >= ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR} still not found after install attempt. Aborting."
            all_ok=false
        fi
    fi

    # ── Node.js ──
    echo ""
    echo -e "  ${BOLD}Checking Node.js...${NC}"

    if ! command -v node &>/dev/null; then
        log_fail "$YELLOW" "NODE" "Node.js not found"
        install_node || true
        if ! command -v node &>/dev/null; then
            log_fail "$RED" "NODE" "Node.js still not found after install attempt. Aborting."
            all_ok=false
        fi
    fi

    if command -v node &>/dev/null; then
        local node_major
        node_major=$(parse_node_version)
        if [[ -n "$node_major" ]]; then
            if (( node_major >= MIN_NODE_MAJOR )); then
                log_ok "$GREEN" "NODE" "Found Node.js v${node_major} (>= ${MIN_NODE_MAJOR})"
            else
                log_fail "$YELLOW" "NODE" "Found v${node_major} but need >= ${MIN_NODE_MAJOR}"
                install_node || true
                node_major=$(parse_node_version)
                if [[ -n "$node_major" ]] && (( node_major >= MIN_NODE_MAJOR )); then
                    log_ok "$GREEN" "NODE" "Upgraded to v${node_major}"
                else
                    log_fail "$RED" "NODE" "Still v${node_major} after install. Aborting."
                    all_ok=false
                fi
            fi
        else
            log_fail "$RED" "NODE" "Could not parse Node.js version"
            all_ok=false
        fi
    fi

    # ── npm ──
    echo ""
    echo -e "  ${BOLD}Checking npm...${NC}"
    if command -v npm &>/dev/null; then
        local npm_ver
        npm_ver=$(npm --version 2>&1 | head -1)
        log_ok "$GREEN" "NPM" "Found npm v${npm_ver}"
    else
        log_fail "$YELLOW" "NPM" "npm not found (should come with Node)"
        if [[ "$PLATFORM" == "ubuntu" ]]; then
            sudo apt install -y npm 2>/dev/null || true
        fi
        if ! command -v npm &>/dev/null; then
            log_fail "$RED" "NPM" "npm still not available. Aborting."
            all_ok=false
        fi
    fi

    if [[ "$all_ok" == false ]]; then
        echo ""
        echo -e "  ${RED}${BOLD}Prerequisites not met. Fix the above issues and re-run.${NC}"
        echo ""
        exit 1
    fi
}

# =============================================================================
#  PHASE 2: Python Service Setup (runs in subshell for parallel execution)
# =============================================================================

setup_python_service() {
    local name=$1 dir=$2 color=$3
    local venv_dir="$dir/.venv"
    local pip_cmd="$venv_dir/$VENV_BIN/pip"
    local python_cmd="$venv_dir/$VENV_BIN/python"

    # When piped through prefix_output, use plain echo (prefix handles the color tag)
    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}✗ Directory not found: $dir${NC}"
        set_result "$name" "FAIL"
        return 1
    fi

    # Force mode: nuke the venv first to fix corrupt installs
    if [[ "$FORCE" == true ]] && [[ -d "$venv_dir" ]]; then
        echo "Removing existing venv (--force)..."
        rm -rf "$venv_dir"
    fi

    # Create venv if missing
    if [[ ! -d "$venv_dir" ]]; then
        echo "Creating Python venv (using $PYTHON_CMD)..."
        if $PYTHON_CMD -m venv "$venv_dir" 2>&1; then
            echo -e "${GREEN}✓ Venv created${NC}"
        else
            echo -e "${RED}✗ Failed to create venv${NC}"
            set_result "$name" "FAIL"
            return 1
        fi
    else
        echo -e "${GRAY}⊘ Venv already exists (use --force to reinstall)${NC}"
    fi

    # Upgrade pip (suppress output)
    echo "Upgrading pip..."
    "$python_cmd" -m pip install --upgrade pip --quiet 2>&1 | tail -1 || true

    # Install requirements
    if [[ -f "$dir/requirements.txt" ]]; then
        if [[ "$FORCE" == true ]] || [[ ! -f "$venv_dir/.deps-installed" ]]; then
            echo "Installing requirements.txt (this may take a while)..."
            if "$pip_cmd" install -r "$dir/requirements.txt" 2>&1; then
                touch "$venv_dir/.deps-installed"
                echo -e "${GREEN}✓ Dependencies installed${NC}"
                set_result "$name" "OK"
            else
                echo -e "${RED}✗ pip install failed (check $dir/requirements.txt)${NC}"
                set_result "$name" "FAIL"
                return 1
            fi
        else
            echo -e "${GRAY}⊘ Dependencies already installed (use --force to reinstall)${NC}"
            set_result "$name" "OK"
        fi
    else
        echo -e "${RED}✗ No requirements.txt found${NC}"
        set_result "$name" "FAIL"
        return 1
    fi
}

# =============================================================================
#  PHASE 3: Node Service Setup (runs in subshell for parallel execution)
# =============================================================================

setup_node_service() {
    local name=$1 dir=$2 color=$3

    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}✗ Directory not found: $dir${NC}"
        set_result "$name" "FAIL"
        return 1
    fi

    # Force mode: nuke node_modules
    if [[ "$FORCE" == true ]] && [[ -d "$dir/node_modules" ]]; then
        echo "Removing node_modules (--force)..."
        rm -rf "$dir/node_modules"
    fi

    if [[ ! -d "$dir/node_modules" ]]; then
        echo "Running npm install..."
        if (cd "$dir" && npm install 2>&1); then
            echo -e "${GREEN}✓ Node dependencies installed${NC}"
            set_result "$name" "OK"
        else
            echo -e "${RED}✗ npm install failed${NC}"
            set_result "$name" "FAIL"
            return 1
        fi
    else
        echo -e "${GRAY}⊘ node_modules already exists (use --force to reinstall)${NC}"
        set_result "$name" "OK"
    fi
}

# =============================================================================
#  MAIN
# =============================================================================

detect_platform

log_header "Nexar Development Environment Setup"
echo ""
log_info "Project root: $SCRIPT_DIR"
log_info "Platform:     $PLATFORM ($OSTYPE)"
log_info "Venv bin:     .venv/$VENV_BIN/"
log_info "Pkg manager:  $PKG_MGR"
if [[ -n "$TARGET_SERVICE" ]]; then
    log_info "Target:       $TARGET_SERVICE only"
fi
if [[ "$FORCE" == true ]]; then
    echo -e "  ${YELLOW}Force mode:   ON (recreating venvs/node_modules from scratch)${NC}"
fi

# ── Phase 1: Prerequisites ──
if [[ "$SKIP_PREREQS" == true ]]; then
    log_header "Prerequisites (skipped)"
    PYTHON_CMD=$(find_python_cmd)
    if [[ -z "$PYTHON_CMD" ]]; then
        echo -e "  ${RED}Python not found and --skip-prereqs set. Cannot continue.${NC}"
        exit 1
    fi
    log_info "Using: $PYTHON_CMD"
else
    log_header "Prerequisites"
    check_prerequisites
    # PYTHON_CMD was set during check_prerequisites
fi

# ── Helper: stream output with color-coded prefix ──
# Pipes stdin through sed, prepending a colored [SERVICE] tag to every line.
# Usage: some_command 2>&1 | prefix_output "$COLOR" "SERVICE-NAME"
prefix_output() {
    local color=$1 name=$2
    local prefix
    # Build the prefix string with ANSI codes for sed
    # Using printf to embed the escape codes into a variable
    prefix=$(printf '  \033[%sm[%s]\033[0m ' "${color}" "${name}")
    sed -u "s|^|${prefix}|"
}

# Map service names to raw ANSI color codes (for sed — can't use \033[...m bash vars inside sed easily)
# These are the numeric codes without the \033[ prefix
declare -A PY_COLOR_CODES
PY_COLOR_CODES["ai-code-converter"]="1;33"
PY_COLOR_CODES["code-analysis-engine"]="0;35"
PY_COLOR_CODES["decision-engine"]="0;34"
PY_COLOR_CODES["hardware-abstraction-layer"]="1;37"

declare -A NODE_COLOR_CODES
NODE_COLOR_CODES["api"]="0;32"
NODE_COLOR_CODES["frontend"]="0;36"

# Corresponding bash color vars for log_ok/log_fail calls
declare -A PY_SERVICE_MAP
PY_SERVICE_MAP["ai-code-converter"]="$YELLOW"
PY_SERVICE_MAP["code-analysis-engine"]="$MAGENTA"
PY_SERVICE_MAP["decision-engine"]="$BLUE"
PY_SERVICE_MAP["hardware-abstraction-layer"]="$WHITE"

declare -A NODE_SERVICE_MAP
NODE_SERVICE_MAP["api"]="$GREEN"
NODE_SERVICE_MAP["frontend"]="$CYAN"

# ── Phase 2: Python Services (parallel with live streaming logs) ──
log_header "Python Services (installing in parallel)"
echo ""

PYTHON_PIDS=()
PYTHON_SERVICES=()

for svc_name in ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer; do
    if should_setup "$svc_name"; then
        svc_color="${PY_SERVICE_MAP[$svc_name]}"
        color_code="${PY_COLOR_CODES[$svc_name]}"

        # Launch in background, pipe output through color-coded prefix in real-time
        (setup_python_service "$svc_name" "$svc_name" "$svc_color" 2>&1) | prefix_output "$color_code" "$svc_name" &
        PYTHON_PIDS+=($!)
        PYTHON_SERVICES+=("$svc_name")
    fi
done

# Wait for all Python services
if [[ ${#PYTHON_PIDS[@]} -gt 0 ]]; then
    for i in "${!PYTHON_PIDS[@]}"; do
        wait "${PYTHON_PIDS[$i]}" 2>/dev/null || true
    done
    echo ""
fi

# ── Phase 3: Node Services (parallel with live streaming logs) ──
log_header "Node.js Services (installing in parallel)"
echo ""

NODE_PIDS=()
NODE_SERVICES=()

for svc_name in api frontend; do
    if should_setup "$svc_name"; then
        svc_color="${NODE_SERVICE_MAP[$svc_name]}"
        color_code="${NODE_COLOR_CODES[$svc_name]}"

        (setup_node_service "$svc_name" "$svc_name" "$svc_color" 2>&1) | prefix_output "$color_code" "$svc_name" &
        NODE_PIDS+=($!)
        NODE_SERVICES+=("$svc_name")
    fi
done

if [[ ${#NODE_PIDS[@]} -gt 0 ]]; then
    for i in "${!NODE_PIDS[@]}"; do
        wait "${NODE_PIDS[$i]}" 2>/dev/null || true
    done
    echo ""
fi

# ── Phase 4: Summary ──
log_header "Setup Summary"

ALL_SERVICES=(ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer api frontend)
ALL_OK=true
SETUP_COUNT=0
OK_COUNT=0

for name in "${ALL_SERVICES[@]}"; do
    if ! should_setup "$name"; then continue; fi
    SETUP_COUNT=$((SETUP_COUNT + 1))

    status=$(get_result "$name")
    if [[ "$status" == "OK" ]]; then
        echo -e "  ${GREEN}✓${NC} $name"
        OK_COUNT=$((OK_COUNT + 1))
    elif [[ "$status" == "FAIL" ]]; then
        echo -e "  ${RED}✗${NC} $name"
        ALL_OK=false
    else
        echo -e "  ${GRAY}?${NC} $name ${GRAY}(not run)${NC}"
    fi
done

echo ""
echo -e "  ${GRAY}Results: ${OK_COUNT}/${SETUP_COUNT} services set up successfully${NC}"
echo ""

if [[ "$ALL_OK" == true && "$SETUP_COUNT" -gt 0 ]]; then
    echo -e "  ${GREEN}${BOLD}All services are set up! Run ${WHITE}bash start-dev.sh${GREEN} to start them.${NC}"
else
    echo -e "  ${YELLOW}${BOLD}Some services had issues. Check the logs above.${NC}"
    echo -e "  ${GRAY}Tip: run ${WHITE}bash setup-dev.sh --force <service-name>${GRAY} to recreate a broken venv${NC}"
fi
echo ""

# Cleanup temp dir
rm -rf "$RESULTS_DIR" 2>/dev/null || true
