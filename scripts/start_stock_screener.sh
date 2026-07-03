#!/bin/bash
# Start Stock Screener application

STOCK_SCREENER_DIR="/media/starscream/wheeljack1/projects/stock-screener"
cd "$STOCK_SCREENER_DIR" || exit 1

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Warning: No virtual environment found in $STOCK_SCREENER_DIR"
fi

# Start the application
python app.py --port 5004
