#!/bin/bash
# Start Open Notebook Docker container with proper configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Use API tunnel URL if available, fallback to localhost
API_URL="${TUNNEL_NOTEBOOK_API_URL:-http://localhost:5055}"

echo "Starting Open Notebook with API URL: $API_URL"

docker run --rm --name open-notebook \
    -p 8502:8502 \
    -p 5055:5055 \
    -v ./notebook_data:/app/data \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    -e TAVILY_API_KEY="$TAVILY_API_KEY" \
    -e SURREAL_USER=root \
    -e SURREAL_PASS=root \
    -e SURREAL_NAMESPACE=terrarium \
    -e SURREAL_DATABASE=notebook \
    -e API_URL="$API_URL" \
    lfnovo/open_notebook:v1-latest-single
