#!/bin/bash
# Run Meanwhile - Matrix-style terminal screensaver with live news

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
MEANWHILE_DIR="$SCRIPT_DIR/utils/meanwhile"

# Check if meanwhile.py exists
if [ ! -f "$MEANWHILE_DIR/meanwhile.py" ]; then
    echo "❌ Meanwhile not found at $MEANWHILE_DIR/meanwhile.py"
    exit 1
fi

# Check if TAVILY_API_KEY is set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "⚠️  TAVILY_API_KEY not set - will use RSS feeds only"
    echo ""
fi

# Run meanwhile
echo "🌐 Launching Meanwhile..."
echo "Press 'q' to quit, 't' to edit topics, 'g' to edit places"
echo ""

python3 "$MEANWHILE_DIR/meanwhile.py" "$@"
