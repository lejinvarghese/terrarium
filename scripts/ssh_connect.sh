#!/bin/bash
# Get SSH connection command for external access

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Load libraries
source "$SCRIPT_DIR/lib/common.sh"

SESSION_NAME="terrarium-tunnel-ssh"

if ! session_exists "$SESSION_NAME"; then
    echo "❌ SSH tunnel not running"
    echo ""
    echo "Start it with: ./dev up"
    exit 1
fi

tunnel_url=$(get_tunnel_url "$SESSION_NAME")

if [ -z "$tunnel_url" ]; then
    echo "⏳ SSH tunnel starting... (try again in a few seconds)"
    exit 1
fi

echo "🔐 SSH Connection:"
echo ""
echo "ssh -o ProxyCommand='cloudflared access tcp --hostname %h' starscream@$tunnel_url"
echo ""
echo "💡 Add to ~/.ssh/config:"
echo ""
echo "Host cybertron-remote"
echo "    HostName $tunnel_url"
echo "    User starscream"
echo "    ProxyCommand cloudflared access tcp --hostname %h"
echo ""
echo "Then just: ssh cybertron-remote"
