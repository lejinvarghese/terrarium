#!/bin/bash
# Stop all Terrarium services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Load libraries
source "$SCRIPT_DIR/../lib/common.sh"
source "$SCRIPT_DIR/../lib/services.conf"
source "$SCRIPT_DIR/../lib/service_manager.sh"

echo "🛑 Stopping Terrarium services..."
STOPPED=0

# Stop all core services
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    # Special cleanup for notebook (stop docker container)
    if [ "$name" = "notebook" ]; then
        if stop_service "$session" "$display_name" "docker stop open-notebook"; then
            STOPPED=1
        fi
    else
        if stop_service "$session" "$display_name"; then
            STOPPED=1
        fi
    fi
done

# Stop all tunnels
for tunnel in "${TUNNELS[@]}"; do
    IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"
    if stop_service "$session" "Tunnel ($display_name)"; then
        STOPPED=1
    fi
done

if [ $STOPPED -eq 0 ]; then
    echo "No Terrarium sessions found"
fi
