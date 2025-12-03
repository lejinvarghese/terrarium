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

echo "🌿 Initializing Terrarium."
echo ""

# Load environment variables
load_env

# Start core services (except archive which needs API tunnel URL first)
echo "⚙️  Starting core services."
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    # Skip archive - we'll start it after API tunnel is ready
    if [ "$name" = "archive" ]; then
        continue
    fi

    start_service "$name" "$session" "$display_name" "$command" "$working_dir"
done
echo ""

# Arrays to collect tunnel URLs for combined notification
NOTIFY_NAMES=()
NOTIFY_URLS=()

# Create tunnels in order: dome first, then archive-api (capture URL), then archive service, then archive tunnel
echo "🌐 Opening public portals."
for tunnel in "${TUNNELS[@]}"; do
    IFS='|' read -r name session display_name port emoji notify <<< "$tunnel"

    # Create dome tunnel first
    if [ "$name" = "dome" ]; then
        create_tunnel "$session" "$port" "$display_name" "false" "$emoji" "DOME_TUNNEL_URL"
        if [ -n "$DOME_TUNNEL_URL" ] && [ "$notify" = "true" ]; then
            NOTIFY_NAMES+=("Dome")
            NOTIFY_URLS+=("$DOME_TUNNEL_URL")
        fi

    # Create archive-api tunnel and capture URL for archive service
    elif [ "$name" = "archive-api" ]; then
        create_tunnel "$session" "$port" "$display_name" "$notify" "$emoji" "TUNNEL_ARCHIVE_API_URL"

        # Wait and retry until API tunnel URL is captured
        RETRY_COUNT=0
        while [ -z "$TUNNEL_ARCHIVE_API_URL" ] && [ $RETRY_COUNT -lt 5 ]; do
            sleep 2
            TUNNEL_ARCHIVE_API_URL=$(get_tunnel_url "$session")
            RETRY_COUNT=$((RETRY_COUNT + 1))
        done

        if [ -z "$TUNNEL_ARCHIVE_API_URL" ]; then
            echo "  ⚠️  API tunnel timeout, using localhost"
            export TUNNEL_ARCHIVE_API_URL="http://localhost:5055"
        fi

        # Export for archive startup script
        export TUNNEL_ARCHIVE_API_URL

        # Now start the archive service with the API tunnel URL
        echo ""
        echo "📚 Initializing Archive."
        for service in "${SERVICES[@]}"; do
            IFS='|' read -r name session display_name command working_dir <<< "$service"
            if [ "$name" = "archive" ]; then
                # Create tmux session and set environment variable before running command
                tmux new-session -d -s "$session" -c "${working_dir:-$(pwd)}"
                tmux send-keys -t "$session" "export TUNNEL_ARCHIVE_API_URL='$TUNNEL_ARCHIVE_API_URL'" C-m
                tmux send-keys -t "$session" "$command" C-m
                echo "  ✓ $display_name"
                sleep 3  # Give archive time to start before creating its tunnel
                break
            fi
        done
        echo ""

    # Create archive tunnel last (after archive service is up)
    elif [ "$name" = "archive" ]; then
        create_tunnel "$session" "$port" "$display_name" "false" "$emoji" "ARCHIVE_TUNNEL_URL"
        if [ -n "$ARCHIVE_TUNNEL_URL" ] && [ "$notify" = "true" ]; then
            NOTIFY_NAMES+=("Archive")
            NOTIFY_URLS+=("$ARCHIVE_TUNNEL_URL")
        fi

    # Create SSH tunnel for remote access
    elif [ "$name" = "ssh" ]; then
        create_tunnel "$session" "$port" "$display_name" "false" "$emoji" "SSH_TUNNEL_URL"
    fi
done

# Send combined notification for all public portals (only if we have URLs)
if [ ${#NOTIFY_URLS[@]} -gt 0 ]; then
    # Verify all URLs are non-empty
    ALL_URLS_VALID=true
    for url in "${NOTIFY_URLS[@]}"; do
        if [ -z "$url" ]; then
            ALL_URLS_VALID=false
            break
        fi
    done

    if [ "$ALL_URLS_VALID" = true ]; then
        # Build arguments: name1 url1 name2 url2 .
        NOTIFY_ARGS=()
        for i in "${!NOTIFY_NAMES[@]}"; do
            NOTIFY_ARGS+=("${NOTIFY_NAMES[$i]}" "${NOTIFY_URLS[$i]}")
        done
        python3 scripts/notify_tunnel.py --combined "${NOTIFY_ARGS[@]}" 2>/dev/null &
    fi
fi

echo ""
echo "✨ Terrarium is alive"
echo ""
echo "  dev status  - View all services"
echo "  dev attach  - Connect to a service"
echo "  dev down    - Stop everything"
