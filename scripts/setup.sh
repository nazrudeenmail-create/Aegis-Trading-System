#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────
# Aegis Trading System — Linux / Codespace / Oracle Cloud Setup
# ───────────────────────────────────────────────────────────────
# This script sets up the full ATS development environment.
#
# It checks for required tools, installs dependencies,
# and verifies everything is ready for development.
#
# Works on:
#   - GitHub Codespaces
#   - Oracle Cloud Linux instances
#   - Any Linux / macOS machine
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
#
# Alternative — run individual steps:
#   ./scripts/setup.sh --backend-only
#   ./scripts/setup.sh --frontend-only
# ───────────────────────────────────────────────────────────────

set -e  # Exit immediately on any error

# ── Parse Arguments ─────────────────────────────────────────────

BACKEND_ONLY=false
FRONTEND_ONLY=false

for arg in "$@"; do
    case $arg in
        --backend-only)  BACKEND_ONLY=true ;;
        --frontend-only) FRONTEND_ONLY=true ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: ./scripts/setup.sh [--backend-only] [--frontend-only]"
            exit 1
            ;;
    esac
done

# ── Resolve Project Root ─────────────────────────────────────────
# Works no matter where you run the script from

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ── Color Helpers ────────────────────────────────────────────────

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
RESET='\033[0m'

print_line()   { echo -e "${CYAN}═══════════════════════════════════════════════${RESET}"; }
print_green()  { echo -e "  ${GREEN}$1${RESET}"; }
print_red()    { echo -e "  ${RED}$1${RESET}"; }
print_yellow() { echo -e "${YELLOW}$1${RESET}"; }
print_gray()   { echo -e "  ${GRAY}$1${RESET}"; }
print_cyan()   { echo -e "${CYAN}  $1${RESET}"; }

echo ""
print_line
echo -e "${CYAN}  Aegis Trading System — Development Setup${RESET}"
print_line
echo ""

# ── Step 1: Check Required Tools ────────────────────────────────

print_yellow "[1/5] Checking required tools..."
echo ""

ALL_OK=true

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if [ "$FRONTEND_ONLY" = false ]; then
    if command_exists python3; then
        PY_VER=$(python3 --version | sed 's/Python //')
        print_green "Python  : $PY_VER   OK"
    else
        print_red "Python  : NOT FOUND   Install: sudo apt install python3"
        ALL_OK=false
    fi

    if command_exists pip3 || command_exists pip; then
        print_green "pip     : Found        OK"
    else
        print_red "pip     : NOT FOUND   Install: sudo apt install python3-pip"
        ALL_OK=false
    fi
fi

if [ "$BACKEND_ONLY" = false ]; then
    if command_exists node; then
        NODE_VER=$(node --version | sed 's/v//')
        print_green "Node.js : $NODE_VER       OK"
    else
        print_red "Node.js : NOT FOUND   Install from https://nodejs.org/ (LTS v20+)"
        ALL_OK=false
    fi

    if command_exists npm; then
        NPM_VER=$(npm --version)
        print_green "npm     : $NPM_VER        OK"
    else
        print_red "npm     : NOT FOUND   Install Node.js first"
        ALL_OK=false
    fi
fi

if command_exists docker; then
    DOCKER_VER=$(docker --version | sed 's/Docker version //')
    print_green "Docker  : $DOCKER_VER"
else
    echo -e "  ${YELLOW}Docker  : NOT FOUND   Install Docker or Docker Desktop${RESET}"
    echo -e "  ${YELLOW}          Docker is only needed for container-based development.${RESET}"
fi

if [ "$ALL_OK" = false ]; then
    echo ""
    print_red "Please install the missing tools listed above, then re-run this script."
    exit 1
fi

# ── Step 2: Backend Setup ────────────────────────────────────────

if [ "$FRONTEND_ONLY" = false ]; then
    echo ""
    print_yellow "[2/5] Setting up backend..."

    cd "$PROJECT_ROOT/backend"

    # Resolve pip command (python3 -m pip is safest on Linux)
    PIP_CMD="python3 -m pip"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_gray "Creating Python virtual environment..."
        python3 -m venv venv
    else
        print_gray "Virtual environment already exists — skipping creation."
    fi

    # Activate virtual environment
    # shellcheck source=/dev/null
    source venv/bin/activate

    print_gray "Installing Python dependencies..."
    pip install -r requirements.txt --quiet

    # Copy .env if it doesn't exist
    if [ ! -f ".env" ]; then
        print_gray "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "  ${YELLOW}⚠  Edit backend/.env to configure your database connection.${RESET}"
    else
        print_gray ".env already exists — skipping."
    fi

    print_green "Backend setup complete."
fi

# ── Step 3: Frontend Setup ───────────────────────────────────────

if [ "$BACKEND_ONLY" = false ]; then
    echo ""
    print_yellow "[3/5] Setting up frontend..."

    cd "$PROJECT_ROOT/frontend"

    print_gray "Installing Node.js dependencies..."
    npm install --silent

    # Copy .env if it doesn't exist
    if [ ! -f ".env" ]; then
        print_gray "Creating .env from .env.example..."
        cp .env.example .env
    else
        print_gray ".env already exists — skipping."
    fi

    print_green "Frontend setup complete."
fi

# ── Step 4: Verify Setup ─────────────────────────────────────────

echo ""
print_yellow "[4/5] Verifying setup..."

cd "$PROJECT_ROOT"

if [ "$FRONTEND_ONLY" = false ]; then
    print_gray "Testing Python imports..."
    cd "$PROJECT_ROOT/backend"

    # Activate venv in case this step runs standalone
    # shellcheck source=/dev/null
    source venv/bin/activate

    IMPORT_RESULT=$(python3 -c "
from app.core.config import get_settings
from app.main import app
print('OK')
" 2>&1)

    if echo "$IMPORT_RESULT" | grep -q "OK"; then
        print_green "Backend imports: OK"
    else
        print_red "Backend imports: FAILED"
        print_red "$IMPORT_RESULT"
    fi
fi

# ── Step 5: Next Steps ───────────────────────────────────────────

cd "$PROJECT_ROOT"

echo ""
print_yellow "[5/5] Setup complete!"
echo ""
print_line
print_cyan "Next steps:"
echo ""
echo -e "  Start backend:"
print_gray "cd backend && source venv/bin/activate"
print_gray "uvicorn app.main:app --reload --port 8000"
echo ""
echo -e "  Start frontend (separate terminal):"
print_gray "cd frontend"
print_gray "npm run dev"
echo ""
echo -e "  Open browser:"
print_gray "Frontend: http://localhost:5173"
print_gray "Backend : http://localhost:8000/docs"
echo ""
echo -e "  Docker (all services at once):"
print_gray "docker compose up"
echo ""
print_line
echo ""
