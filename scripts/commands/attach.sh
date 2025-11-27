#!/bin/bash
# Attach to a specific service tmux session

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Load libraries
source "$SCRIPT_DIR/../lib/common.sh"
source "$SCRIPT_DIR/../lib/services.conf"

SERVICE="$1"

if [ -z "$SERVICE" ]; then
    echo "Error: Please specify a service to attach to"
    echo "Usage: dev attach <service>"
    echo ""
    echo "Available services:"
    for service in "${SERVICES[@]}"; do
        IFS='|' read -r name session display_name command working_dir <<< "$service"
        echo "  - $name"
    done
    echo ""
    echo "Available tunnels:"
    for tunnel in "${TUNNELS[@]}"; do
        IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"
        echo "  - $name"
    done
    exit 1
fi

# Get session name from service map
SESSION="${SERVICE_MAP[$SERVICE]}"

if [ -z "$SESSION" ]; then
    echo "Error: Invalid service '$SERVICE'"
    echo "Run 'dev attach' without arguments to see available services"
    exit 1
fi

if session_exists "$SESSION"; then
    tmux attach-session -t "$SESSION"
else
    echo "Error: Session '$SESSION' does not exist. Run 'dev up' first."
    exit 1
fi
