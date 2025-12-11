#!/bin/bash
# Stop all Terrarium services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Load libraries
source "$SCRIPT_DIR/../lib/common.sh"
source "$SCRIPT_DIR/../lib/services.conf"
source "$SCRIPT_DIR/../lib/service_manager.sh"
source "$SCRIPT_DIR/../lib/tunnel_manager.sh"

# Load environment
load_env

echo "🛑 Stopping Terrarium services."
STOPPED=0

# First, ensure docker container is stopped (regardless of tmux session state)
if docker ps -q -f name=open-notebook | grep -q .; then
    docker stop open-notebook >/dev/null 2>&1
    docker rm open-notebook >/dev/null 2>&1
    echo "🛑 Stopped Archive container"
    STOPPED=1
fi

# Stop all core services
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    if stop_service "$session" "$display_name"; then
        STOPPED=1
    fi
done

# Stop tunnels (named or legacy quick tunnels)
if is_named_tunnel_configured; then
    # Stop single named tunnel
    if stop_named_tunnel; then
        STOPPED=1
    fi
else
    # Stop all legacy quick tunnels
    for tunnel in "${TUNNELS[@]}"; do
        IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"
        if stop_service "$session" "Tunnel ($display_name)"; then
            STOPPED=1
        fi
    done
fi

if [ $STOPPED -eq 0 ]; then
    echo "No Terrarium sessions found"
fi
