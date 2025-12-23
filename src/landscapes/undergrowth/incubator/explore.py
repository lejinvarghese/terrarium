#!/usr/bin/env python3
"""Simple exploration runner for incubator agents"""

import random
import click
from src.core.environment import Environment
from src.landscapes.undergrowth.incubator.config import (
    LANDSCAPE_NAME,
    LANDSCAPE_DISPLAY_NAME,
    MODEL_NAME,
    DEFAULT_EPISODE_STEPS,
)
from src.landscapes.undergrowth.incubator.agents import agent_registry


def generate_dynamic_objective(agent_id: str, model) -> str:
    """Generate a dynamic exploration objective for an agent"""
    agent_config = agent_registry.get_config(agent_id)
    agent_name = agent_config.get("name", agent_id)
    focus_areas = agent_config.get("focus", "general exploration")

    # Example objective templates based on agent focus
    templates = [
        f"Explore recent developments in {focus_areas}",
        f"Search for interesting papers or articles about {focus_areas}",
        f"Investigate new techniques or methods in {focus_areas}",
        f"Find and analyze emerging trends in {focus_areas}",
        f"Discover novel applications or use cases in {focus_areas}",
    ]

    # Pick a random template
    objective = random.choice(templates)

    return objective


def run_episode(
    agent_id: str,
    objective: str,
    steps: int = DEFAULT_EPISODE_STEPS,
    timeout: int = 60,
    epsilon: float = 0.1,
    model = None,
):
    """Run a simple exploration episode"""
    agent_config = agent_registry.get_config(agent_id)

    click.secho(f"\n[Agent] {agent_config['name']}", fg="green", bold=True)
    click.secho(f"[Objective] {objective}", fg="yellow")

    env = Environment(
        agent_id=agent_id,
        agent_config=agent_config,
        model_name=MODEL_NAME,
        landscape_name=LANDSCAPE_NAME,
        timeout=timeout,
    )

    env.reset(objective)

    # Simple step loop - first step uses objective, rest continue exploring
    for step_num in range(1, steps + 1):
        prompt = None if step_num == 1 else "Continue exploring this topic deeper."
        result = env.step(prompt)

        if result["done"]:
            click.secho(f"\n[Episode] Stopped at step {step_num}", fg="yellow")
            break

    summary = env.close()
    return summary


@click.command()
@click.option(
    "--agent",
    "-a",
    type=click.Choice(list(agent_registry.agents.keys())),
    required=True,
    help="Agent to run",
)
@click.option(
    "--objective",
    "-o",
    required=True,
    help="What to explore (be specific!)",
)
@click.option(
    "--steps",
    "-s",
    default=DEFAULT_EPISODE_STEPS,
    help="Number of exploration steps",
)
@click.option(
    "--timeout",
    "-t",
    default=60,
    help="Timeout per step in seconds",
)
def explore(agent: str, objective: str, steps: int, timeout: int):
    """Run agent exploration episode

    Example:
        python explore.py -a A001 -o "Search arxiv for quantum computing papers from 2024"
    """
    click.secho("\n" + "=" * 60, fg="cyan")
    click.secho(f"{LANDSCAPE_DISPLAY_NAME} - Exploration", fg="cyan", bold=True)
    click.secho("=" * 60 + "\n", fg="cyan")

    run_episode(agent, objective, steps, timeout)


if __name__ == "__main__":
    explore()
