#!/bin/bash
# Common utility functions for Terrarium dev environment

# Load environment variables from .env file
load_env() {
    local env_file="${1:-.env}"
    if [ -f "$env_file" ]; then
        export $(grep -v '^#' "$env_file" | xargs)
    fi
}

# Check if tmux session exists
session_exists() {
    tmux has-session -t "$1" 2>/dev/null
}

# Output helpers
echo_success() { echo "✅ $1"; }
echo_error() { echo "❌ $1"; }
echo_warning() { echo "⚠️  $1"; }
echo_info() { echo "   $1"; }

# Check if tmux is installed
check_tmux() {
    if ! command -v tmux &> /dev/null; then
        echo "Error: tmux is not installed. Install it with: sudo apt install tmux"
        exit 1
    fi
}

# Extract tunnel URL from tmux session
get_tunnel_url() {
    local session="$1"
    tmux capture-pane -t "$session" -p -S -200 -J 2>/dev/null | \
        grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | \
        head -1
}
