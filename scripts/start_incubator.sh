#!/bin/bash
# Convenience wrapper for incubator scheduler

cd /media/starscream/bumblebee1/blaze/terrarium
PYTHONPATH=. uv run python src/landscapes/undergrowth/incubator/scheduler.py "$@"
