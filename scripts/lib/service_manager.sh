#!/bin/bash
# Service lifecycle management functions

# Start a service in a tmux session
# Args: name, session, display_name, command, [working_dir]
start_service() {
    local name="$1"
    local session="$2"
    local display_name="$3"
    local command="$4"
    local working_dir="${5:-$(pwd)}"

    if session_exists "$session"; then
        echo_warning "Session '$session' already exists"
        return 0
    fi

    tmux new-session -d -s "$session" -c "$working_dir"
    tmux send-keys -t "$session" "$command" C-m
    echo_success "Started $display_name in session '$session'"
}

# Stop a service and kill its tmux session
# Args: session, display_name, [cleanup_command]
stop_service() {
    local session="$1"
    local display_name="$2"
    local cleanup_command="${3:-}"

    if session_exists "$session"; then
        # Run cleanup if provided
        if [ -n "$cleanup_command" ]; then
            eval "$cleanup_command" 2>/dev/null
        fi

        tmux kill-session -t "$session"
        echo_success "Stopped $display_name"
        return 0
    fi
    return 1
}

# Check and display service status
# Args: session, display_name, [info_callback]
service_status() {
    local session="$1"
    local display_name="$2"
    local info_callback="${3:-}"

    if session_exists "$session"; then
        echo_success "$display_name - running (session: $session)"

        # Call info callback if provided (for displaying URLs, etc)
        if [ -n "$info_callback" ] && type "$info_callback" &>/dev/null; then
            "$info_callback" "$session"
        fi
        return 0
    else
        echo_error "$display_name - not running"
        return 1
    fi
}
