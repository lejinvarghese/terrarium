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

# Load environment
load_env

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

if is_named_tunnel_configured; then
    # Check named tunnel
    if session_exists "terrarium-tunnel"; then
        echo "  ✅ Named Tunnel Active"
        echo ""
        echo "  Your services are available at:"
        echo "    🌐 Web       → https://${TUNNEL_DOMAIN}"
        echo "    🤖 Dome      → https://dome.${TUNNEL_DOMAIN}"
        echo "    📚 Archive   → https://archive.${TUNNEL_DOMAIN}"
        echo "    🔌 API       → https://api.${TUNNEL_DOMAIN}"
        echo "    🔐 SSH       → ssh.${TUNNEL_DOMAIN}"
        ANY_RUNNING=1
    else
        echo "  ✗ Named Tunnel"
        echo "    (Domain: ${TUNNEL_DOMAIN})"
    fi
else
    # Check legacy quick tunnels
    for tunnel in "${TUNNELS[@]}"; do
        IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"

        if session_exists "$session"; then
            tunnel_url=$(get_tunnel_url "$session")
            if [ -n "$tunnel_url" ]; then
                echo "  $emoji $display_name"
                echo "     $tunnel_url"

                # Special handling for SSH tunnel
                if [ "$name" = "ssh" ]; then
                    echo "     ssh -o ProxyCommand='cloudflared access tcp --hostname %h' starscream@$tunnel_url"
                fi
            else
                echo "  ⏳ $display_name (waiting...)"
            fi
            ANY_RUNNING=1
        else
            echo "  ✗ $display_name"
        fi
    done

    echo ""
    echo "  💡 Tip: Run './dev setup' to configure permanent domain URLs"
fi

if [ $ANY_RUNNING -eq 0 ]; then
    echo ""
    echo "Nothing running. Use 'dev up' to start."
fi
