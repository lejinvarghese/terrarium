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

# Start core services (except archive and web)
echo "⚙️  Starting core services."
for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"

    # Skip archive - we'll start it after API tunnel is ready
    # Skip web - we'll start it last after other services stabilize
    if [ "$name" = "archive" ] || [ "$name" = "web" ]; then
        continue
    fi

    start_service "$name" "$session" "$display_name" "$command" "$working_dir"

    # Wait for Qdrant to initialize before starting dependent services
    if [ "$name" = "qdrant" ]; then
        echo "  ⏳ Waiting for Qdrant to initialize..."
        sleep 3

        # Verify Qdrant is responding
        if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
            echo "  ✅ Qdrant ready"
        else
            echo "  ⚠️  Qdrant may still be initializing (services will retry)"
        fi
    fi
done
echo ""

# Start Archive service (only with named tunnel; legacy mode starts it later)
if is_named_tunnel_configured; then
    echo "📚 Initializing Archive."
    # With named tunnel, use fixed API subdomain
    export TUNNEL_ARCHIVE_API_URL="https://api.${TUNNEL_DOMAIN}"

    for service in "${SERVICES[@]}"; do
        IFS='|' read -r name session display_name command working_dir <<< "$service"
        if [ "$name" = "archive" ]; then
            # Create tmux session and set environment variable before running command
            tmux new-session -d -s "$session" -c "${working_dir:-$(pwd)}"
            sleep 0.5  # Wait for shell to be ready
            tmux send-keys -t "$session" "" C-m  # Send blank line to ensure shell is ready
            tmux send-keys -t "$session" "export TUNNEL_ARCHIVE_API_URL='$TUNNEL_ARCHIVE_API_URL'" C-m
            tmux send-keys -t "$session" "$command" C-m
            echo "  ✓ $display_name (API: https://api.${TUNNEL_DOMAIN}, UI: https://archive.${TUNNEL_DOMAIN})"
            sleep 5  # Give archive time to start both API (5055) and UI (8502)
            break
        fi
    done
    echo ""
fi

# Start web service last (after other services stabilize)
echo "🖥️  Initializing Web."
echo "  ⏳ Waiting for services to stabilize..."
sleep 5  # 5 second delay to let other services start

for service in "${SERVICES[@]}"; do
    IFS='|' read -r name session display_name command working_dir <<< "$service"
    if [ "$name" = "web" ]; then
        start_service "$name" "$session" "$display_name" "$command" "$working_dir"
        sleep 3  # Give web time to start
        break
    fi
done
echo ""

# Check if named tunnel is configured
if is_named_tunnel_configured; then
    # Use named tunnel (single tunnel for all services)
    echo "🌐 Opening public portals."
    echo ""
    start_named_tunnel

    # Send notification with domain URLs (TEMPORARILY DISABLED)
    # if [ -n "$TUNNEL_DOMAIN" ]; then
    #     python3 scripts/notify_tunnel.py \
    #         --combined \
    #         "Web" "https://${TUNNEL_DOMAIN}" \
    #         "Dome" "https://dome.${TUNNEL_DOMAIN}" \
    #         "Archive" "https://archive.${TUNNEL_DOMAIN}" \
    #         2>/dev/null &
    # fi
else
    # Legacy: Use separate quick tunnels for each service
    echo "🌐 Opening quick tunnels (run './dev setup' to configure permanent URLs)"
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
                sleep 0.5  # Wait for shell to be ready
                tmux send-keys -t "$session" "" C-m  # Send blank line to ensure shell is ready
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

    # Create web tunnel (service already started)
    elif [ "$name" = "web" ]; then
        create_tunnel "$session" "$port" "$display_name" "false" "$emoji" "WEB_TUNNEL_URL"
        if [ -n "$WEB_TUNNEL_URL" ] && [ "$notify" = "true" ]; then
            NOTIFY_NAMES+=("Web")
            NOTIFY_URLS+=("$WEB_TUNNEL_URL")
        fi

    # Create SSH tunnel for remote access
    elif [ "$name" = "ssh" ]; then
        create_tunnel "$session" "$port" "$display_name" "false" "$emoji" "SSH_TUNNEL_URL"
    fi
done

# Send combined notification for all public portals (TEMPORARILY DISABLED)
# if [ ${#NOTIFY_URLS[@]} -gt 0 ]; then
#     # Verify all URLs are non-empty
#     ALL_URLS_VALID=true
#     for url in "${NOTIFY_URLS[@]}"; do
#         if [ -z "$url" ]; then
#             ALL_URLS_VALID=false
#             break
#         fi
#     done
#
#     if [ "$ALL_URLS_VALID" = true ]; then
#         # Build arguments: name1 url1 name2 url2 .
#         NOTIFY_ARGS=()
#         for i in "${!NOTIFY_NAMES[@]}"; do
#             NOTIFY_ARGS+=("${NOTIFY_NAMES[$i]}" "${NOTIFY_URLS[$i]}")
#         done
#         python3 scripts/notify_tunnel.py --combined "${NOTIFY_ARGS[@]}" 2>/dev/null &
#     fi
# fi
fi  # End of named tunnel check

echo ""
echo "✨ Terrarium is alive"
echo ""
echo "  dev status  - View all services"
echo "  dev attach  - Connect to a service"
echo "  dev down    - Stop everything"
