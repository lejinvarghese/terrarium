#!/bin/bash
# Cloudflare tunnel management functions

# Create a cloudflare tunnel
# Args: session_name, port, service_display_name, [send_notification], [emoji], [return_url_var_name]
create_tunnel() {
    local session_name="$1"
    local port="$2"
    local service_name="$3"
    local send_notification="${4:-false}"
    local emoji="${5:-🌐}"
    local return_var="${6:-}"

    if session_exists "$session_name"; then
        # Check if existing session has a valid tunnel URL
        local existing_url=$(get_tunnel_url "$session_name")
        if [ -n "$existing_url" ]; then
            echo "  ✓ $service_name already active"
            # Return existing URL if requested
            if [ -n "$return_var" ]; then
                eval "$return_var='$existing_url'"
            fi
            return 0
        else
            # Session exists but no valid tunnel, kill and recreate
            tmux kill-session -t "$session_name" 2>/dev/null
            sleep 1
        fi
    fi

    tmux new-session -d -s "$session_name"
    tmux send-keys -t "$session_name" "~/.local/bin/cloudflared tunnel --url http://localhost:$port" C-m

    # Wait and retry to get tunnel URL
    local tunnel_url=""
    local retry=0
    while [ -z "$tunnel_url" ] && [ $retry -lt 8 ]; do
        sleep 1
        tunnel_url=$(get_tunnel_url "$session_name")
        retry=$((retry + 1))
    done

    if [ -n "$tunnel_url" ]; then
        echo "  $emoji $service_name: $tunnel_url"

        # Return URL via variable name if requested
        if [ -n "$return_var" ]; then
            eval "$return_var='$tunnel_url'"
        fi
    else
        echo "  ⏳ $service_name (waiting for URL...)"
        # Return empty if requested
        if [ -n "$return_var" ]; then
            eval "$return_var=''"
        fi
    fi
}

# Display tunnel status with URL
# Args: session
tunnel_status_info() {
    local session="$1"
    local tunnel_url=$(get_tunnel_url "$session")

    if [ -n "$tunnel_url" ]; then
        # Determine emoji based on session name
        local emoji="🌐"
        [[ "$session" == *"api"* ]] && emoji="🔌"
        [[ "$session" == *"archive"* ]] && emoji="📓"

        echo_info "$emoji Public URL: $tunnel_url"
    fi
}
