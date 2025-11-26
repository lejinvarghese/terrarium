#!/bin/bash
# Check status of all Terrarium services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Load libraries
source "$SCRIPT_DIR/../lib/common.sh"
source "$SCRIPT_DIR/../lib/services.conf"
source "$SCRIPT_DIR/../lib/service_manager.sh"
source "$SCRIPT_DIR/../lib/tunnel_manager.sh"

echo "Terrarium Services Status:"
echo ""

ANY_RUNNING=0

# Check core services
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    # Special info for notebook
    if [ "$name" = "notebook" ]; then
        if service_status "$session" "$display_name"; then
            echo_info "📓 Web UI: http://localhost:8502"
            echo_info "🔌 API: http://localhost:5055"
            ANY_RUNNING=1
        fi
    else
        if service_status "$session" "$display_name"; then
            ANY_RUNNING=1
        fi
    fi
done

# Check tunnels
for tunnel in "${TUNNELS[@]}"; do
    IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"
    if service_status "$session" "Tunnel $display_name" "tunnel_status_info"; then
        ANY_RUNNING=1
    fi
done

if [ $ANY_RUNNING -eq 0 ]; then
    echo ""
    echo "No services are running. Use 'dev up' to start."
fi
