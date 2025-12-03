#!/bin/bash
# Create SSH tunnel for external access
# This creates a persistent cloudflare tunnel for SSH access from anywhere

SESSION_NAME="terrarium-tunnel-ssh"
PORT=22
SERVICE_NAME="SSH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Load common utilities
source "$SCRIPT_DIR/lib/common.sh"

# Check if session already exists
if session_exists "$SESSION_NAME"; then
    existing_url=$(get_tunnel_url "$SESSION_NAME")
    if [ -n "$existing_url" ]; then
        echo "✅ SSH tunnel already active:"
        echo "   $existing_url"
        echo ""
        echo "📝 To connect:"
        echo "   ssh -o ProxyCommand='cloudflared access tcp --hostname %h' starscream@$existing_url"
        exit 0
    else
        # Kill stale session
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null
        sleep 1
    fi
fi

# Create new tunnel
echo "🔐 Creating SSH tunnel..."
tmux new-session -d -s "$SESSION_NAME"
tmux send-keys -t "$SESSION_NAME" "~/.local/bin/cloudflared tunnel --url tcp://localhost:$PORT" C-m

# Wait for tunnel URL
tunnel_url=""
retry=0
while [ -z "$tunnel_url" ] && [ $retry -lt 10 ]; do
    sleep 1
    tunnel_url=$(get_tunnel_url "$SESSION_NAME")
    retry=$((retry + 1))
done

if [ -n "$tunnel_url" ]; then
    echo "✅ SSH tunnel created!"
    echo "   $tunnel_url"
    echo ""
    echo "📝 To connect from anywhere:"
    echo "   ssh -o ProxyCommand='cloudflared access tcp --hostname %h' starscream@$tunnel_url"
    echo ""
    echo "💡 Or use the tunnel directly (requires cloudflared on your laptop):"
    echo "   ssh starscream@localhost -p \$(cloudflared access tcp --hostname $tunnel_url --url localhost:2222 &>/dev/null & echo 2222)"
else
    echo "⚠️  Failed to create tunnel"
    exit 1
fi
