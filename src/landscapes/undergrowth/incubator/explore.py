#!/usr/bin/env python3
"""Exploration runner using RL-style environment"""

import click
import random

from src.core.environment import ExplorationEnvironment
from src.core.database import DatabaseManager
from src.core.tools import get_tools
from src.core.landscapes import get_observations_path, get_memory_path
from src.landscapes.undergrowth.incubator.config import (
    LANDSCAPE_NAME,
    LANDSCAPE_DISPLAY_NAME,
    MODEL_NAME,
    DEFAULT_EPISODE_STEPS,
    DEFAULT_EPSILON,
)
from src.landscapes.undergrowth.incubator.agents import get_agent_config, get_registry


STEP_PROMPTS = [
    "Now explore a different aspect or related topic. What else is interesting?",
    "Go deeper on something you mentioned. Ask 'why' or 'how' questions.",
    "Compare and contrast what you've learned. What patterns do you see?",
    "Find something surprising or unexpected. Look for contradictions.",
    "Synthesize what you've learned. What's the bigger picture?",
]

RANDOM_PROMPTS = [
    "Follow a tangent. Pick something unrelated and see where it leads.",
    "Ask a completely different question. What would a child be curious about?",
    "What's the weirdest thing you could explore right now?",
    "Pick a random word from what you've learned and dive deep into just that.",
    "What question would surprise you the most to answer?",
    "Explore the opposite of what you've been learning about.",
    "Find a connection between this topic and something completely unrelated.",
    "What would happen if the main assumption you've been using was wrong?",
    "Explore the most obscure detail you've encountered so far.",
    "What does this topic remind you of? Follow that association.",
]


def run_episode(
    agent_id: str,
    objective: str,
    steps: int = DEFAULT_EPISODE_STEPS,
    timeout: int = 180,
    epsilon: float = DEFAULT_EPSILON,
):
    db_manager = DatabaseManager(get_observations_path(LANDSCAPE_NAME))
    tools = get_tools()
    agent_config = get_agent_config(agent_id)

    env = ExplorationEnvironment(
        agent_id=agent_id,
        agent_config=agent_config,
        model_name=MODEL_NAME,
        memory_db_path=get_memory_path(LANDSCAPE_NAME),
        db_manager=db_manager,
        tools=tools,
        timeout=timeout,
    )

    env.reset(objective)
    click.secho(
        f"[Episode] Exploration strategy: ε={epsilon:.2f} (random exploration probability)",
        fg="cyan",
    )

    for step_num in range(1, steps + 1):
        if step_num == 1:
            prompt = None
        else:
            if random.random() < epsilon:
                prompt = random.choice(RANDOM_PROMPTS)
                click.secho(f"[ε-explore] Using random prompt", fg="magenta", dim=True)
            else:
                prompt_idx = min(step_num - 2, len(STEP_PROMPTS) - 1)
                prompt = STEP_PROMPTS[prompt_idx]

        result = env.step(prompt)

        if result["done"]:
            click.secho(
                f"\n[Episode] Terminating early at step {step_num}", fg="yellow"
            )
            break

    summary = env.close()
    return summary


@click.command()
@click.option(
    "--agent",
    "-a",
    type=click.Choice(list(get_registry().agents.keys())),
    required=True,
    help="Agent to run",
)
@click.option(
    "--objective",
    "-o",
    default="Explore and learn about nature, animals, and the world around you",
    help="Exploration objective",
)
@click.option(
    "--steps", "-s", default=DEFAULT_EPISODE_STEPS, help="Number of steps per episode"
)
@click.option("--timeout", "-t", default=30, help="Timeout per step in seconds")
@click.option(
    "--epsilon",
    "-e",
    default=DEFAULT_EPSILON,
    type=float,
    help="Random exploration probability (0.0-1.0)",
)
def explore(agent: str, objective: str, steps: int, timeout: int, epsilon: float):
    """Run agent exploration episode"""
    click.secho("\n" + "=" * 60, fg="cyan")
    click.secho(
        f"{LANDSCAPE_DISPLAY_NAME} - Exploration Environment", fg="cyan", bold=True
    )
    click.secho("=" * 60 + "\n", fg="cyan")
    run_episode(agent, objective, steps, timeout, epsilon)


if __name__ == "__main__":
    explore()
