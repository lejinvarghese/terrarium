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
        echo_warning "Session '$session_name' already exists"
        return 0
    fi

    tmux new-session -d -s "$session_name"
    tmux send-keys -t "$session_name" "~/.local/bin/cloudflared tunnel --url http://localhost:$port" C-m
    sleep 4

    # Extract tunnel URL
    local tunnel_url=$(get_tunnel_url "$session_name")

    if [ -n "$tunnel_url" ]; then
        echo_success "Started Tunnel ($service_name) in session '$session_name'"
        echo_info "$emoji Public URL: $tunnel_url"

        # Send Telegram notification if requested
        if [ "$send_notification" = "true" ]; then
            python3 scripts/notify_tunnel.py "$tunnel_url" "$service_name" 2>/dev/null &
        fi

        # Return URL via variable name if requested
        if [ -n "$return_var" ]; then
            eval "$return_var='$tunnel_url'"
        fi
    else
        echo_success "Started Tunnel ($service_name) in session '$session_name' (URL pending...)"
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
        [[ "$session" == *"notebook"* ]] && emoji="📓"

        echo_info "$emoji Public URL: $tunnel_url"
    fi
}
