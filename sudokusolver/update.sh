#!/usr/bin/env bash
# Sudoku Tutor — update script (Mac / Linux)
# Pulls the latest code and refreshes dependencies.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Sudoku Tutor — update ==="

echo "Pulling latest code ..."
git -C "$REPO_ROOT" pull

echo "Updating dependencies ..."
cd "$SCRIPT_DIR"
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

echo "Update complete."
