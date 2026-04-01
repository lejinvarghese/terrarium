#!/bin/bash
# Landscape management router

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

python3 "$PROJECT_ROOT/scripts/landscapes.py" "$@"
