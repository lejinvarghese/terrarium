#!/bin/bash
# Terrarium 3D Visualization Launcher

echo "🌿 Starting Terrarium 3D Visualization..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start the development server
echo "🚀 Launching visualization..."
echo "   Opening at http://localhost:3000"
echo ""
echo "   Controls:"
echo "   - Left Mouse: Rotate"
echo "   - Right Mouse: Pan"
echo "   - Scroll: Zoom"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

npm run dev
