#!/usr/bin/env bash
# Sudoku Tutor — one-line installer (Mac / Linux)
# Usage (from repo root):  bash sudokusolver/install.sh
# Usage (from this dir):   bash install.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Sudoku Tutor — install ==="

# Require Python 3.8+
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.8+ and try again." >&2
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(sys.version_info >= (3, 8))")
if [ "$PY_VER" != "True" ]; then
    echo "ERROR: Python 3.8+ required." >&2
    exit 1
fi

echo "Creating virtual environment in .venv/ ..."
python3 -m venv .venv

echo "Installing dependencies ..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

chmod +x launch.sh update.sh

echo ""
echo "Done!  Run:  bash sudokusolver/launch.sh"
echo "       or:   bash launch.sh  (from this directory)"
