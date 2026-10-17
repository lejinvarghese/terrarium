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

# Stop all core services (Archive and World Monitor cleanup handle their Docker containers)
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    cleanup_command=""
    if [ "$name" = "monitor" ]; then
        # tmux kill-session only kills the `docker compose logs -f` pane — the
        # containers themselves run under dockerd and survive that. Tear them
        # down explicitly, same reasoning as archive's docker cleanup on start.
        cleanup_command="cd '$PROJECT_ROOT/${working_dir:-.}' && docker compose down"
    fi

    if stop_service "$session" "$display_name" "$cleanup_command"; then
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
