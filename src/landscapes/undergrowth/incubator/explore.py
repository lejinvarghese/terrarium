#!/usr/bin/env python3
"""Simple exploration runner for incubator agents"""

import asyncio
import random
import click
from datetime import datetime

from src.core.goals import GoalGenerator
from src.landscapes.core.agent import BaseAgent
from src.landscapes.undergrowth.incubator.config import (
    LANDSCAPE_NAME,
    LANDSCAPE_DISPLAY_NAME,
    MODEL_NAME,
    TEACHER_MODEL,
    DEFAULT_EPISODE_STEPS,
)
from src.landscapes.undergrowth.incubator.agents import agent_registry


def generate_dynamic_objective(agent_id: str, model=None, epsilon: float = 0.2) -> str:
    """Generate a dynamic exploration objective for an agent.

    Args:
        agent_id: Agent identifier
        model: Unused (kept for compatibility)
        epsilon: Exploration rate (0.0-1.0)

    Returns:
        Goal string for the agent
    """
    agent_config = agent_registry.get_config(agent_id)
    goal_gen = GoalGenerator(epsilon=epsilon)
    return goal_gen.generate(agent_config)


async def run_episode(
    agent_id: str,
    objective: str = None,
    steps: int = DEFAULT_EPISODE_STEPS,
    timeout: int = 60,
    epsilon: float = 0.2,
    model_type: str = "openrouter",
    model_name: str = None,
):
    """Run an exploration episode for an agent.

    Args:
        agent_id: Agent identifier (e.g., "A001")
        objective: Exploration goal (auto-generated if None)
        steps: Number of exploration steps
        timeout: Timeout per step in seconds
        epsilon: Exploration rate for goal generation
        model_type: "openrouter" (teacher/Grok) or "ollama" (student/local)
        model_name: Override default model name

    Returns:
        Episode summary dict
    """
    agent_config = agent_registry.get_config(agent_id)

    # Generate objective if not provided
    if objective is None:
        objective = generate_dynamic_objective(agent_id, epsilon=epsilon)

    # Determine model name based on type
    if model_name is None:
        if model_type == "openrouter":
            model_name = TEACHER_MODEL  # Teacher model (Claude)
        else:
            model_name = MODEL_NAME  # Local student model

    # Display episode info
    model_display = f"{model_type}:{model_name}"
    click.secho(f"\n{'=' * 60}", fg="cyan")
    click.secho(f"Agent: {agent_config['name']} ({agent_id})", fg="green", bold=True)
    click.secho(f"Model: {model_display}", fg="blue")
    click.secho(f"Goal: {objective}", fg="yellow")
    click.secho(f"{'=' * 60}\n", fg="cyan")

    # Create agent
    agent = await BaseAgent.create(
        id=agent_id,
        name=agent_config["name"],
        user_id=agent_id,  # Use agent_id as user_id for separate memories
        instructions=agent_config["persona_template"],
        model_name=model_name,
        model_type=model_type,
        debug=False,
        skip_logging=False,  # Enable logging to database
    )

    try:
        # Step 1: Initial exploration with objective
        click.secho(f"[Step 1/{steps}] Starting exploration...", fg="cyan")
        response = await agent.run(objective)
        click.secho(f"\n{response.content}\n", fg="white")

        # Subsequent steps: natural continuation
        for step_num in range(2, steps + 1):
            click.secho(f"[Step {step_num}/{steps}] Continuing...", fg="cyan")

            # Natural follow-up prompts
            prompts = [
                "Based on what you found, what else would you like to explore?",
                "What did you learn? What are you curious about next?",
                "Reflect on what you discovered. What patterns or connections do you notice?",
                "What questions arose from your exploration? Pick one to investigate.",
            ]
            followup = random.choice(prompts)

            response = await agent.run(followup)
            click.secho(f"\n{response.content}\n", fg="white")

        # Final reflection
        click.secho(f"[Reflection] Summarizing episode...", fg="cyan")
        reflection_prompt = (
            "Reflect on this exploration episode. What did you learn? "
            "What was most interesting or surprising? What would you explore next time?"
        )
        response = await agent.run(reflection_prompt)
        click.secho(f"\n{response.content}\n", fg="white")

        click.secho(f"\n{'=' * 60}", fg="cyan")
        click.secho(f"Episode complete!", fg="green", bold=True)
        click.secho(f"{'=' * 60}\n", fg="cyan")

        return {
            "agent_id": agent_id,
            "agent_name": agent_config["name"],
            "objective": objective,
            "steps": steps,
            "model_type": model_type,
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
        }

    finally:
        # Clean up MCP connections
        await agent.close()


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
    default=None,
    help="What to explore (auto-generated if not provided)",
)
@click.option(
    "--steps",
    "-s",
    default=DEFAULT_EPISODE_STEPS,
    help="Number of exploration steps",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(["teacher", "student", "openrouter", "ollama"]),
    default="teacher",
    help="Model to use: teacher (Grok via OpenRouter) or student (local)",
)
@click.option(
    "--epsilon",
    "-e",
    default=0.2,
    type=float,
    help="Exploration rate for goal generation (0.0-1.0)",
)
def explore(agent: str, objective: str, steps: int, model: str, epsilon: float):
    """Run agent exploration episode

    Examples:
        # Run Nyx with auto-generated goal using Grok (teacher)
        uv run python -m src.landscapes.undergrowth.incubator.explore -a A001

        # Run Anya with specific goal using local model (student)
        uv run python -m src.landscapes.undergrowth.incubator.explore -a A002 -m student -o "Find ambient electronic music"

        # Run Sage with high exploration rate
        uv run python -m src.landscapes.undergrowth.incubator.explore -a A003 -e 0.5
    """
    click.secho("\n" + "=" * 60, fg="cyan")
    click.secho(f"{LANDSCAPE_DISPLAY_NAME} - Exploration", fg="cyan", bold=True)
    click.secho("=" * 60 + "\n", fg="cyan")

    # Map friendly names to model types
    model_type_map = {
        "teacher": "openrouter",
        "student": "ollama",
        "openrouter": "openrouter",
        "ollama": "ollama",
    }
    model_type = model_type_map[model]

    # Run episode
    asyncio.run(run_episode(
        agent_id=agent,
        objective=objective,
        steps=steps,
        model_type=model_type,
        epsilon=epsilon,
    ))


if __name__ == "__main__":
    explore()
