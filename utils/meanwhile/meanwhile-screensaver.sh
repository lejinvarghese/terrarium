#!/bin/bash
# Meanwhile screensaver - Multi-monitor with xdotool positioning

LOCK_FILE="/tmp/meanwhile-screensaver.lock"

# Function to clean up on exit
cleanup() {
    rm -f "$LOCK_FILE"
}

# Check if meanwhile terminals are already running
if pgrep -f "gnome-terminal.*Meanwhile" > /dev/null; then
    echo "Meanwhile screensaver already running"
    exit 0
fi

# Check stale lock file
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "Meanwhile screensaver script already running (PID: $PID)"
        exit 0
    else
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"
trap cleanup EXIT INT TERM

# Get monitor information from xrandr
MONITORS_INFO=$(xrandr --query | grep " connected" | while read -r line; do
    NAME=$(echo "$line" | awk '{print $1}')
    GEOMETRY=$(echo "$line" | grep -oP '\d+x\d+\+\d+\+\d+' | head -1)

    if [ -n "$GEOMETRY" ]; then
        WIDTH=$(echo "$GEOMETRY" | cut -d'x' -f1)
        REST=$(echo "$GEOMETRY" | cut -d'x' -f2)
        HEIGHT=$(echo "$REST" | cut -d'+' -f1)
        X_OFFSET=$(echo "$REST" | cut -d'+' -f2)
        Y_OFFSET=$(echo "$REST" | cut -d'+' -f3)

        echo "$NAME $WIDTH $HEIGHT $X_OFFSET $Y_OFFSET"
    fi
done)

MONITOR_COUNT=$(echo "$MONITORS_INFO" | wc -l)
echo "Launching meanwhile on $MONITOR_COUNT monitor(s)..."

# Launch meanwhile on each monitor
MONITOR_NUM=0
while read -r NAME WIDTH HEIGHT X_OFF Y_OFF; do
    ((MONITOR_NUM++))

    echo "  Monitor $MONITOR_NUM ($NAME): ${WIDTH}x${HEIGHT} at +${X_OFF}+${Y_OFF}"

    # Launch terminal in fullscreen
    gnome-terminal --full-screen \
                   --hide-menubar \
                   --title="Meanwhile-$NAME" \
                   -- bash -c "meanwhile; exit" &

    # Wait for window to appear and become fullscreen
    sleep 1

    # Find the window ID
    WID=$(xdotool search --name "Meanwhile-$NAME" | tail -1)

    if [ -n "$WID" ]; then
        # Move the fullscreen window to the correct monitor position
        xdotool windowmove "$WID" "$X_OFF" "$Y_OFF"

        echo "    ✓ Fullscreen on monitor $MONITOR_NUM"
    else
        echo "    ✗ Could not find window for $NAME"
    fi

done <<< "$MONITORS_INFO"

echo "Meanwhile launched. Monitoring processes..."

# Keep script alive while meanwhile terminals are running
# This keeps the lock file active and prevents multiple spawns
while pgrep -f "gnome-terminal.*Meanwhile" > /dev/null || pgrep -f "^meanwhile$" > /dev/null; do
    sleep 2
done

echo "All meanwhile instances closed."
# Cleanup via trap
