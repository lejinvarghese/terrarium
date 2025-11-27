#!/bin/bash
# Open WebUI startup script
# Usage: ./start-open-webui.sh
# To update: ./start-open-webui.sh --update

set -e  # Exit on error

# Configuration
export DATA_DIR="${DATA_DIR:-$HOME/.open-webui}"
PORT="${PORT:-8080}"
VENV_DIR="${HOME}/.local/open-webui-venv"

echo "Starting Open WebUI."
echo "Data directory: $DATA_DIR"

# Check if we should update
if [[ "$1" == "--update" ]]; then
    echo "Updating Open WebUI."
    python3.11 -m pip install --upgrade open-webui
fi

# Create venv and install if it doesn't exist
if [[ ! -d "$VENV_DIR" ]]; then
    echo "First time setup - creating virtual environment."
    python3.11 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install uv
    uv pip install open-webui
else
    source "$VENV_DIR/bin/activate"
fi

# Start Open WebUI server
echo "Starting server on port $PORT."
open-webui serve --port "$PORT"
