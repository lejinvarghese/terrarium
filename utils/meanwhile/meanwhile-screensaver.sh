#!/bin/bash
# Meanwhile screensaver - Single instance protection

LOCK_FILE="/tmp/meanwhile-screensaver.lock"

# Function to clean up on exit
cleanup() {
    rm -f "$LOCK_FILE"
    pkill -f "gnome-terminal.*Meanwhile" 2>/dev/null
}

# Check if already running
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "Meanwhile screensaver already running (PID: $PID)"
        exit 0
    else
        # Stale lock file, remove it
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file with our PID
echo $$ > "$LOCK_FILE"

# Set up cleanup on exit
trap cleanup EXIT INT TERM

# Kill any orphaned meanwhile terminals
pkill -f "gnome-terminal.*Meanwhile" 2>/dev/null || true

# Get monitor count
MONITOR_COUNT=$(xrandr --query | grep " connected" | wc -l)

echo "Launching meanwhile on $MONITOR_COUNT monitor(s)..."

# Launch meanwhile on each monitor
for ((i=1; i<=MONITOR_COUNT; i++)); do
    gnome-terminal --full-screen \
                   --hide-menubar \
                   --title="Meanwhile-$i" \
                   -- bash -c "meanwhile; exit" &
    sleep 0.3
done

# Wait for all terminal processes to finish
# This keeps the lock file active while meanwhile is running
wait

# Cleanup happens automatically via trap
