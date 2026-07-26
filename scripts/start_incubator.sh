#!/bin/bash
# Convenience wrapper for the incubator daily runner (incubate.py).
# Distinct from the main Terrarium scheduler engine (src/engine/scheduler.py).

cd /media/starscream/bumblebee1/blaze/terrarium
PYTHONPATH=. uv run python -m src.landscapes.undergrowth.incubator.incubate "$@"
