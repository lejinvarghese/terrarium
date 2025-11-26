#!/bin/bash
# Start all Terrarium services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Load libraries
source "$SCRIPT_DIR/../lib/common.sh"
source "$SCRIPT_DIR/../lib/services.conf"
source "$SCRIPT_DIR/../lib/service_manager.sh"
source "$SCRIPT_DIR/../lib/tunnel_manager.sh"

# Check prerequisites
check_tmux

echo "🌿 Starting Terrarium services"

# Load environment variables
load_env

# Start all core services
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"
    start_service "$name" "$session" "$display_name" "$command" "$working_dir"
done

# Create tunnels
for tunnel in "${TUNNELS[@]}"; do
    IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"

    # Special handling for API tunnel - capture URL for notebook
    if [ "$name" = "notebook-api" ]; then
        create_tunnel "$session" "$port" "$display_name" "$notify" "$emoji" "TUNNEL_NOTEBOOK_API_URL"

        # Wait extra time to ensure API tunnel URL is captured
        if [ -z "$TUNNEL_NOTEBOOK_API_URL" ]; then
            echo "⏳ Waiting for API tunnel URL..."
            sleep 3
            TUNNEL_NOTEBOOK_API_URL=$(get_tunnel_url "$session")
        fi

        # Export for notebook startup script
        export TUNNEL_NOTEBOOK_API_URL
    else
        create_tunnel "$session" "$port" "$display_name" "$notify" "$emoji"
    fi
done

echo ""
echo_success "All services started in separate tmux sessions"
echo_info "Use 'dev attach <service>' to view a specific service"
echo_info "Use 'dev status' to see all running services"
echo_info "Use 'dev down' to stop all services"
