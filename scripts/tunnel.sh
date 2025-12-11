#!/bin/bash
# Network tunneling helper for local services
# Usage:
#   ./tunnel.sh [PORT]           - Show connection info
#   ./tunnel.sh local [PORT]     - Show local WiFi URL
#   ./tunnel.sh internet [PORT]  - Start internet tunnel
#   ./tunnel.sh public [PORT]    - Alias for internet

set -e

PORT="${2:-${1:-8080}}"
COMMAND="${1:-info}"

# If first arg is a number, treat as port and show info
if [[ "$COMMAND" =~ ^[0-9]+$ ]]; then
    PORT="$COMMAND"
    COMMAND="info"
fi

# Get local IP (first non-docker IP)
LOCAL_IP=$(hostname -I | awk '{print $1}')

case "$COMMAND" in
    local)
        echo "📱 Local WiFi Access:"
        echo ""
        echo "   http://$LOCAL_IP:$PORT"
        echo ""
        echo "Open this URL on any device connected to your WiFi"
        ;;

    internet|public|tunnel)
        echo "🌐 Starting internet tunnel for port $PORT."
        echo ""
        echo "Your service will be accessible from anywhere via a public URL"
        echo "Press Ctrl+C to stop the tunnel"
        echo ""

        # Add ssh.localhost.run to known_hosts to avoid prompt
        ssh-keyscan -H ssh.localhost.run >> ~/.ssh/known_hosts 2>/dev/null || true

        # Start tunnel
        ssh -R 80:localhost:$PORT ssh.localhost.run
        ;;

    info|*)
        echo "================================"
        echo "Network Access - Port $PORT"
        echo "================================"
        echo ""
        echo "📱 Local WiFi (same network):"
        echo "   http://$LOCAL_IP:$PORT"
        echo ""
        echo "🌐 Internet Tunnel (anywhere):"
        echo "   ./tunnel.sh internet $PORT"
        echo ""
        echo "Commands:"
        echo "  ./tunnel.sh local $PORT      - Show local URL"
        echo "  ./tunnel.sh internet $PORT   - Start public tunnel"
        ;;
esac
