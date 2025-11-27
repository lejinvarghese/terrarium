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

echo "🌿 Terrarium Status"
echo ""

ANY_RUNNING=0

# Check core services
echo "Services:"
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    if session_exists "$session"; then
        echo "  ✓ $display_name"
        ANY_RUNNING=1
    else
        echo "  ✗ $display_name"
    fi
done

# Check tunnels
echo ""
echo "Public Portals:"
for tunnel in "${TUNNELS[@]}"; do
    IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"

    if session_exists "$session"; then
        tunnel_url=$(get_tunnel_url "$session")
        if [ -n "$tunnel_url" ]; then
            echo "  $emoji $display_name"
            echo "     $tunnel_url"
        else
            echo "  ⏳ $display_name (waiting.)"
        fi
        ANY_RUNNING=1
    else
        echo "  ✗ $display_name"
    fi
done

if [ $ANY_RUNNING -eq 0 ]; then
    echo ""
    echo "Nothing running. Use 'dev up' to start."
fi
