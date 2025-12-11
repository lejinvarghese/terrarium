#!/bin/bash
# Start Qdrant server in Docker with persistent storage

set -e

STORAGE_DIR="$(pwd)/data/qdrant_storage"

# Ensure storage directory exists
mkdir -p "$STORAGE_DIR"

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q '^qdrant-terrarium$'; then
    echo "🔄 Existing container found, removing..."
    docker rm -f qdrant-terrarium 2>/dev/null || true
fi

echo "🚀 Starting Qdrant server..."

# Start Qdrant server with persistent storage
docker run -d \
  --name qdrant-terrarium \
  -p 6333:6333 \
  -p 6334:6334 \
  -v "$STORAGE_DIR:/qdrant/storage" \
  --restart unless-stopped \
  qdrant/qdrant:latest

# Wait for server to initialize
echo "⏳ Waiting for Qdrant to initialize..."
sleep 3

# Check if server is responding
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo "✅ Qdrant server is running"
    curl -s http://localhost:6333/collections | head -5
else
    echo "⚠️  Qdrant server may still be initializing..."
fi

# Follow logs
echo ""
echo "📋 Following Qdrant logs (Ctrl+C to detach):"
docker logs -f qdrant-terrarium
