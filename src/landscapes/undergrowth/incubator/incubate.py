#!/usr/bin/env python3
"""Daily runner for the incubator colony.

Named `incubate` (not `scheduler`) to keep it distinct from the main Terrarium
scheduler engine at `src/engine/scheduler.py`.

Runs every agent once per cycle, serially (one small model, one GPU). The
default cadence is daily, so each agent explores once a day and continues from
its journal the next day. Agents share one Store, so notes written this cycle
are visible to agents that run later in the same cycle.

Usage:
  # one cycle now (ideal for cron: `@daily`), then exit
  python -m src.landscapes.undergrowth.incubator.incubate --once

  # run continuously, one cycle every N hours (default 24)
  python -m src.landscapes.undergrowth.incubator.incubate --interval-hours 24
"""

import logging
import signal
import sys
import time
from pathlib import Path

import click

from src.landscapes.undergrowth.incubator.agents import agent_registry
from src.landscapes.undergrowth.incubator.config import DEFAULT_EPISODE_STEPS, MODEL_NAME
from src.landscapes.undergrowth.incubator.explore import run_episode
from src.landscapes.undergrowth.incubator.store import Store

LOG_PATH = Path(__file__).parent / "incubate.log"
_stop = False


def _handle_stop(signum, frame):
    global _stop
    logging.info("signal %s received — will stop after current agent", signum)
    _stop = True


def run_cycle(steps: int, model: str) -> None:
    """Run one exploration episode for every agent, serially, sharing a Store."""
    store = Store()
    try:
        for agent_id in agent_registry.list_agents():
            if _stop:
                break
            name = agent_registry.get_config(agent_id)["name"]
            logging.info("[%s] %s starting episode", agent_id, name)
            try:
                result = run_episode(agent_id, steps=steps, model_name=model,
                                     store=store, verbose=False)
                logging.info("[%s] done: %s tool calls in %ss · ep %s",
                             agent_id, result["tool_calls"], result["duration_s"],
                             result["episode_id"])
            except Exception as e:
                logging.error("[%s] episode failed: %s", agent_id, e, exc_info=True)
    finally:
        store.close()


@click.command()
@click.option("--once", is_flag=True, help="Run a single cycle then exit (use with cron).")
@click.option("--interval-hours", default=24.0, help="Hours between cycles when looping.")
@click.option("--steps", default=DEFAULT_EPISODE_STEPS, help="Model turns per episode.")
@click.option("--model", default=MODEL_NAME, help="Ollama model id.")
def main(once, interval_hours, steps, model):
    logging.basicConfig(
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    n = len(agent_registry.list_agents())
    logging.info("incubate start · %d agents · model=%s · %s",
                 n, model, "once" if once else f"every {interval_hours}h")

    run_cycle(steps, model)
    if once:
        logging.info("incubate done (--once)")
        return

    while not _stop:
        wake = time.time() + interval_hours * 3600
        logging.info("next cycle in %.1fh", interval_hours)
        while time.time() < wake and not _stop:
            time.sleep(min(5.0, wake - time.time()))
        if _stop:
            break
        run_cycle(steps, model)

    logging.info("incubate stopped")


if __name__ == "__main__":
    main()
