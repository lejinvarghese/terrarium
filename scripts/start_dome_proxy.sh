#!/bin/bash
# Start Dome auth proxy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/src/auth-proxy"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing auth proxy dependencies..."
    npm install
fi

# Start dome proxy
SERVICE=dome node server.js
