#!/usr/bin/env python3
"""Exploration agent for Incubator using Agno"""

import time
import click
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb

from src.incubator.config import MODEL_NAME, DEFAULT_EPISODE_STEPS, MEMORY_DB
from src.incubator.agents import get_agent_config, AGENTS
from src.incubator.models import add_observation
from src.incubator.tools import get_mcp_tools


def calculate_reward(outcome: str) -> float:
    outcome_lower = outcome.lower()
    if any(x in outcome_lower for x in ["failed", "exception", "timeout", "connection error"]):
        return -0.3
    if any(x in outcome_lower for x in ["found", "discovered", "learned"]):
        return 0.7
    if len(outcome) > 300:
        return 0.7
    return 0.5


def run_agno_exploration(agent_id: str, objective: str, steps: int = DEFAULT_EPISODE_STEPS, timeout: int = 180):
    agent_config = get_agent_config(agent_id)

    click.secho(f"\n[Explore] Model: {MODEL_NAME}", fg="cyan")

    model = Ollama(
        id=MODEL_NAME,
        options={
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "repeat_penalty": 1.0,
            "num_ctx": 4096,
        }
    )

    mcp_tools = get_mcp_tools()
    memory_db = SqliteDb(db_file=str(MEMORY_DB))

    agent = Agent(
        name=agent_config['name'],
        model=model,
        tools=mcp_tools,
        instructions=agent_config['system_prompt'],
        db=memory_db,
        enable_user_memories=True,
        add_memories_to_context=True,
        add_history_to_context=False,
        markdown=True,
        stream_events=True,
        tool_call_limit=5,
        debug_mode=False,
    )

    episode_id = f"{agent_id}_{int(time.time())}"
    click.secho(f"[Explore] Episode: {episode_id}", fg="cyan")
    click.secho(f"[Explore] Objective: {objective}\n", fg="yellow")

    all_results = []
    prompts = [
        "Now explore a different aspect or related topic. What else is interesting?",
        "Go deeper on something you mentioned. Ask 'why' or 'how' questions.",
        "Compare and contrast what you've learned. What patterns do you see?",
        "Find something surprising or unexpected. Look for contradictions.",
        "Synthesize what you've learned. What's the bigger picture?",
    ]

    for iteration in range(1, steps + 1):
        click.secho(f"\n{'='*60}", fg="cyan")
        click.secho(f"Iteration {iteration}/{steps}", fg="cyan", bold=True)
        click.secho(f"{'='*60}", fg="cyan")

        if all_results:
            context = "Previous discoveries:\n" + "\n".join([f"- Step {i+1}: {r[:200]}..." for i, r in enumerate(all_results)])
            iteration_prompt = prompts[min(iteration - 1, len(prompts) - 1)]
            current_task = f"{objective}\n\n{context}\n\n{iteration_prompt}"
        else:
            current_task = objective

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(agent.run, current_task, user_id=episode_id)
                response = future.result(timeout=timeout)

            result_text = response.content if hasattr(response, 'content') and response.content else str(response)

            if not result_text or len(result_text.strip()) == 0:
                result_text = "[Agent returned empty response]"

            all_results.append(result_text)
            click.secho(f"\n[Result]:", fg="green")
            click.secho(result_text[:500] + ("..." if len(result_text) > 500 else ""), fg="white")

        except FuturesTimeoutError:
            click.secho(f"\n[TIMEOUT]: Iteration exceeded {timeout}s", fg="red", bold=True)
            result_text = f"[Iteration timed out after {timeout}s]"
            all_results.append(result_text)

        except Exception as e:
            click.secho(f"\n[ERROR]: {e}", fg="red", bold=True)
            result_text = f"[Error: {str(e)}]"
            all_results.append(result_text)

    result_text = "\n\n=== EXPLORATION SUMMARY ===\n\n".join([f"Step {i+1}:\n{r}" for i, r in enumerate(all_results)])
    reward = calculate_reward(result_text)

    add_observation(
        agent_id=agent_id,
        episode_id=episode_id,
        observation_text=result_text,
        action_code="agent.run(objective)",
        outcome=result_text,
        reward=reward,
    )

    memories = agent.get_user_memories(user_id=episode_id)
    if memories:
        click.secho(f"\n[Memory] Created {len(memories)} memories", fg="cyan")
        for i, mem in enumerate(memories[:10], 1):
            click.secho(f"  {i}. {mem.memory}", fg="white")
        if len(memories) > 10:
            click.secho(f"  ... and {len(memories) - 10} more", fg="white", dim=True)

    click.secho(f"\n[Explore] Complete! (Reward: {reward})", fg="green", bold=True)


@click.command()
@click.option("--agent", "-a", type=click.Choice(list(AGENTS.keys())), required=True)
@click.option("--objective", "-o", default="Explore and learn about nature, animals, and the world around you")
@click.option("--steps", "-s", default=DEFAULT_EPISODE_STEPS)
@click.option("--timeout", "-t", default=180, help="Timeout per iteration in seconds")
def explore(agent: str, objective: str, steps: int, timeout: int):
    click.secho("\n" + "="*60, fg="cyan")
    click.secho("Incubator - Exploration", fg="cyan", bold=True)
    click.secho("="*60 + "\n", fg="cyan")
    run_agno_exploration(agent, objective, steps, timeout)


if __name__ == "__main__":
    explore()
