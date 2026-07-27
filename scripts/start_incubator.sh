#!/bin/bash
# Incubator control wrapper.
#
# Scheduling is now owned by the shared Terrarium engine
# (configs/schedule.json -> "🌱 Incubator - Daily Exploration", daily 06:00),
# NOT by a standalone loop. So the legacy control verbs (start/stop/restart/
# status) are intentionally no-ops here — running a second scheduler would
# double-fire the agents.
#
# Manual runs still work:
#   scripts/start_incubator.sh --once              # one cycle now
#   scripts/start_incubator.sh --interval-hours 24 # standalone loop (only if
#                                                     the engine task is removed)

cd /media/starscream/bumblebee1/blaze/terrarium

case "$1" in
  start|stop|restart|status|"")
    echo "ℹ️  The incubator is scheduled by the Terrarium engine (daily 06:00)."
    echo "    See configs/schedule.json · '🌱 Incubator - Daily Exploration'."
    echo "    For a one-off run:  scripts/start_incubator.sh --once"
    exit 0
    ;;
esac

PYTHONPATH=. uv run python -m src.landscapes.undergrowth.incubator.incubate "$@"
