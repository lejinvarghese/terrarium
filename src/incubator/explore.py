#!/usr/bin/env python3
"""Exploration runner using RL-style environment"""

import click
import random
from src.incubator.config import DEFAULT_EPISODE_STEPS, DEFAULT_EPSILON
from src.incubator.agents import AGENTS
from src.incubator.environment import ExplorationEnvironment


# Structured exploration prompts (exploitation)
STEP_PROMPTS = [
    "Now explore a different aspect or related topic. What else is interesting?",
    "Go deeper on something you mentioned. Ask 'why' or 'how' questions.",
    "Compare and contrast what you've learned. What patterns do you see?",
    "Find something surprising or unexpected. Look for contradictions.",
    "Synthesize what you've learned. What's the bigger picture?",
]

# Random exploration prompts (exploration)
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


def run_episode(agent_id: str, objective: str, steps: int = DEFAULT_EPISODE_STEPS, timeout: int = 180, epsilon: float = DEFAULT_EPSILON):
    """Run a complete exploration episode

    Args:
        agent_id: Agent identifier
        objective: Exploration objective
        steps: Number of steps to run
        timeout: Timeout per step in seconds
        epsilon: Probability of random exploration (0.0 = always structured, 1.0 = always random)
    """
    # Initialize environment
    env = ExplorationEnvironment(agent_id=agent_id, timeout=timeout)

    # Reset for new episode
    env.reset(objective)

    click.secho(f"[Episode] Exploration strategy: ε={epsilon:.2f} (random exploration probability)", fg="cyan")

    # Run episode steps
    for step_num in range(1, steps + 1):
        # Get prompt for this step
        if step_num == 1:
            prompt = None
        else:
            # Epsilon-greedy: random exploration vs structured prompts
            if random.random() < epsilon:
                # Explore: use random tangential prompt
                prompt = random.choice(RANDOM_PROMPTS)
                click.secho(f"[ε-explore] Using random prompt", fg="magenta", dim=True)
            else:
                # Exploit: use structured prompt sequence
                prompt_idx = min(step_num - 2, len(STEP_PROMPTS) - 1)
                prompt = STEP_PROMPTS[prompt_idx]

        # Execute step
        result = env.step(prompt)

        # Check if episode should terminate
        if result["done"]:
            click.secho(f"\n[Episode] Terminating early at step {step_num}", fg="yellow")
            break

    # Close episode
    summary = env.close()

    return summary


@click.command()
@click.option("--agent", "-a", type=click.Choice(list(AGENTS.keys())), required=True, help="Agent to run")
@click.option("--objective", "-o", default="Explore and learn about nature, animals, and the world around you", help="Exploration objective")
@click.option("--steps", "-s", default=DEFAULT_EPISODE_STEPS, help="Number of steps per episode")
@click.option("--timeout", "-t", default=180, help="Timeout per step in seconds")
@click.option("--epsilon", "-e", default=DEFAULT_EPSILON, type=float, help="Random exploration probability (0.0-1.0)")
def explore(agent: str, objective: str, steps: int, timeout: int, epsilon: float):
    """Run agent exploration episode"""

    click.secho("\n" + "="*60, fg="cyan")
    click.secho("Incubator - Exploration Environment", fg="cyan", bold=True)
    click.secho("="*60 + "\n", fg="cyan")

    run_episode(agent, objective, steps, timeout, epsilon)


if __name__ == "__main__":
    explore()
