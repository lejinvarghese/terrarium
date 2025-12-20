#!/usr/bin/env python3
"""Continuous exploration scheduler for incubator agents"""

import heapq
import logging
import random
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from agno.models.ollama import Ollama
from src.core.database import DatabaseManager
from src.core.landscapes import get_observations_path
from src.landscapes.undergrowth.incubator.explore import run_episode, generate_dynamic_objective
from src.landscapes.undergrowth.incubator.agents import agent_registry
from src.landscapes.undergrowth.incubator.config import (
    DEFAULT_EPISODE_STEPS, 
    DEFAULT_EPSILON,
    LANDSCAPE_NAME,
    MODEL_NAME
)

LOG_PATH = Path(__file__).parent / "scheduler.log"

shutdown_requested = False

# Default scheduling parameters
DEFAULT_BASE_INTERVAL_HOURS = 4
DEFAULT_JITTER_HOURS = 1.0
DEFAULT_TIMEOUT = 180


class AgentScheduler:
    """Priority queue-based scheduler for agent exploration"""

    def __init__(self):
        self.queue = []  # heap: [(next_run_time, agent_id, config), ...]
        self.db = DatabaseManager(get_observations_path(LANDSCAPE_NAME))
        self.model = Ollama(
            id=MODEL_NAME, 
            options={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 20,
                "repeat_penalty": 1.0,
                "num_ctx": 4096,
            }
        )

    def get_schedule_config(self, agent_id: str, agent_index: int, total_agents: int) -> dict:
        """Get scheduling configuration for an agent with auto-staggering"""
        # Auto-stagger: distribute agents across time to avoid overlaps
        # Each agent gets progressively longer intervals
        stagger_multiplier = 1 + (agent_index * 0.5)  # 1.0, 1.5, 2.0, ...

        base_interval = DEFAULT_BASE_INTERVAL_HOURS * stagger_multiplier
        jitter = DEFAULT_JITTER_HOURS * stagger_multiplier

        return {
            "base_interval_hours": base_interval,
            "jitter_hours": jitter,
            "steps": DEFAULT_EPISODE_STEPS,
            "epsilon": DEFAULT_EPSILON,
            "timeout": DEFAULT_TIMEOUT,
            "objective": generate_dynamic_objective(agent_id, self.model)
        }

    def calculate_next_run(self, config: dict, is_initial: bool = False) -> datetime:
        """Calculate next run time with random jitter"""
        base_seconds = config["base_interval_hours"] * 3600
        jitter_seconds = random.uniform(
            -config["jitter_hours"] * 3600,
            config["jitter_hours"] * 3600
        )

        if is_initial:
            stagger = random.uniform(0, 60)
            total_seconds = stagger
        else:
            total_seconds = base_seconds + jitter_seconds

        return datetime.now() + timedelta(seconds=total_seconds)

    def schedule_all_agents(self, run_immediately: bool = False):
        """Discover and schedule all agents from registry"""
        agent_ids = list(agent_registry.agents.keys())
        total_agents = len(agent_ids)

        logging.info(f"Discovered {total_agents} agents from registry")

        for idx, agent_id in enumerate(agent_ids):
            config = self.get_schedule_config(agent_id, idx, total_agents)

            if run_immediately:
                next_run = datetime.now() + timedelta(seconds=random.uniform(5, 60))
            else:
                next_run = self.calculate_next_run(config, is_initial=True)

            heapq.heappush(self.queue, (next_run, agent_id, config))

            logging.info(
                f"[{agent_id}] Scheduled - "
                f"Interval: {config['base_interval_hours']:.1f}h ±{config['jitter_hours']:.1f}h, "
                f"First run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
            )

    def run_agent_episode(self, agent_id: str, config: dict):
        """Execute a single agent episode"""
        global shutdown_requested

        if shutdown_requested:
            return

        try:
            # Refresh objective based on latest context
            current_objective = generate_dynamic_objective(agent_id, self.model)
            logging.info(f"[{agent_id}] Starting episode with objective: {current_objective}")
            
            start_time = time.time()

            run_episode(
                agent_id=agent_id,
                objective=current_objective,
                steps=config["steps"],
                timeout=config["timeout"],
                epsilon=config["epsilon"],
                model=self.model,
            )

            duration = time.time() - start_time
            logging.info(f"[{agent_id}] Completed episode in {duration:.1f}s")

        except Exception as e:
            logging.error(f"[{agent_id}] Episode failed: {e}", exc_info=True)

    def run_forever(self):
        """Main scheduler loop"""
        logging.info("Scheduler started")

        while self.queue and not shutdown_requested:
            next_run, agent_id, config = heapq.heappop(self.queue)

            # Wait until scheduled time
            while datetime.now() < next_run and not shutdown_requested:
                wait_seconds = (next_run - datetime.now()).total_seconds()
                if wait_seconds > 0:
                    time.sleep(min(wait_seconds, 1.0))

            if shutdown_requested:
                break

            self.run_agent_episode(agent_id, config)

            # Reschedule with fresh jitter
            new_next_run = self.calculate_next_run(config)
            heapq.heappush(self.queue, (new_next_run, agent_id, config))

            logging.info(
                f"[{agent_id}] Rescheduled - "
                f"Next run: {new_next_run.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        logging.info("Scheduler stopped")


def handle_shutdown(signum, frame):
    """Handle graceful shutdown"""
    global shutdown_requested
    logging.info(f"Received signal {signum}, shutting down...")
    shutdown_requested = True


if __name__ == "__main__":
    # Setup file logging only
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    run_immediately = "--run-immediately" in sys.argv

    scheduler = AgentScheduler()
    scheduler.schedule_all_agents(run_immediately=run_immediately)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    scheduler.run_forever()
    sys.exit(0)
