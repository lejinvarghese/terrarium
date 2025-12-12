#!/usr/bin/env python3
"""Exploration agent for Incubator using Agno - optimized for small models"""

import os
import time
import click
from pathlib import Path

from src.incubator.config import (
    OLLAMA_MODEL,
    DEFAULT_EPISODE_STEPS,
)
from src.incubator.agents import get_agent_config, AGENTS
from src.incubator.models import add_observation
from src.incubator.tools import get_tools


def calculate_reward(action: str, outcome: str) -> float:
    """Calculate reward for an observation."""
    outcome_lower = outcome.lower()

    # Actual execution failures
    if any(x in outcome_lower for x in ["failed", "exception", "timeout", "connection error"]):
        return -0.3

    # High value discoveries
    if any(x in outcome_lower for x in ["found", "discovered", "learned"]):
        return 0.7

    # Substantive content
    if len(outcome) > 300:
        return 0.7

    return 0.5


def run_agno_exploration(
    agent_id: str,
    objective: str,
    steps: int = DEFAULT_EPISODE_STEPS
):
    """Run exploration with Agno + Ollama + MCP"""

    click.secho(f"\n[Explore] Loading Agno framework...", fg="cyan", bold=True)

    try:
        from agno.agent import Agent
        from agno.models.ollama import Ollama
        from agno.tools.mcp import MCPTools
        from mcp import StdioServerParameters
    except ImportError as e:
        click.secho(f"\n[Error] Agno dependencies missing: {e}", fg="red", bold=True)
        click.secho("Install with: pip install agno ollama", fg="yellow")
        click.secho("See: https://github.com/agno-agi/agno", fg="yellow")
        return

    # Get agent configuration
    agent_config = get_agent_config(agent_id)

    click.secho(f"[Explore] Using Ollama model: {OLLAMA_MODEL}", fg="yellow")

    # Initialize Ollama model
    model = Ollama(id=OLLAMA_MODEL)

    click.secho(f"[Explore] Loading MCP servers...", fg="cyan")

    # Get the path to the Terrarium MCP server
    project_root = Path(__file__).parent.parent.parent

    # Define MCP servers
    mcp_configs = {
        "terrarium": {
            "command": "python",
            "args": [str(project_root / "src" / "mcp" / "server.py")],
        },
        "arxiv": {
            "command": "uv",
            "args": [
                "tool", "run", "arxiv-mcp-server",
                "--storage-path", str(Path.home() / ".arxiv-mcp-server" / "papers")
            ],
        },
        "tavily": {
            "command": "/home/starscream/.npm-global/bin/tavily-mcp",
            "args": [],
        },
        "spotify": {
            "command": "/home/starscream/.npm-global/bin/spotify-mcp",
            "args": [],
        },
    }

    # Load MCP tools
    mcp_tools = []
    for server_name, config in mcp_configs.items():
        try:
            click.secho(f"[Explore] Loading {server_name}...", fg="yellow")

            # Create server params
            server_params = StdioServerParameters(
                command=config["command"],
                args=config["args"],
                env={**os.environ}
            )

            # Create MCP tools with server params and timeout
            tools = MCPTools(
                server_params=server_params,
                tool_name_prefix=f"{server_name}_",
                timeout_seconds=30  # 30 second timeout for MCP operations
            )
            mcp_tools.append(tools)
            click.secho(f"[Explore]   ✓ {server_name} loaded", fg="green")
        except Exception as e:
            click.secho(f"[Explore]   ✗ {server_name}: {e}", fg="red")
            continue

    click.secho(f"\n[Explore] Creating {agent_config['name']}...", fg="cyan")

    # Create Agno agent with persona and tools
    # Note: Reasoning mode might be too complex for small 1.5B models
    # Trying simple mode first
    use_reasoning = False  # Set to True to enable reasoning mode

    agent_config_dict = {
        'name': agent_config['name'],
        'model': model,
        'tools': mcp_tools,
        'instructions': agent_config['system_prompt'],
        'markdown': True,
        'stream_intermediate_steps': True,
        'tool_call_limit': 5,  # Limit tool calls to prevent infinite loops
        'debug_mode': True,
    }

    if use_reasoning:
        agent_config_dict.update({
            'reasoning': True,
            'reasoning_min_steps': 1,
            'reasoning_max_steps': steps,
        })

    agent = Agent(**agent_config_dict)

    # Run exploration
    episode_id = f"{agent_id}_{int(time.time())}"
    click.secho(f"[Explore] Episode: {episode_id}\n", fg="cyan")

    # Create task with objective
    task = f"{objective}"

    click.secho(f"[Explore] Objective: {task}\n", fg="yellow")

    # Run agent in iterative mode
    # Since reasoning mode is too complex for small models, we'll iterate manually
    all_results = []

    for iteration in range(1, steps + 1):
        click.secho(f"\n{'='*60}", fg="cyan")
        click.secho(f"Iteration {iteration}/{steps}", fg="cyan", bold=True)
        click.secho(f"{'='*60}", fg="cyan")

        # Build context from previous iterations
        if all_results:
            context = f"Previous discoveries:\n" + "\n".join([f"- Step {i+1}: {r[:200]}..." for i, r in enumerate(all_results)])
            current_task = f"{task}\n\n{context}\n\nContinue exploring and build on what you've learned."
        else:
            current_task = task

        # Run agent for this iteration with timeout
        try:
            click.secho(f"[Running agent...]", fg="yellow")

            # Use signal for timeout (Unix only)
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Agent run exceeded 60 second timeout")

            # Set 60 second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)

            try:
                response = agent.run(current_task)
            finally:
                # Cancel the alarm
                signal.alarm(0)

            # Extract result
            if hasattr(response, 'content') and response.content:
                result_text = response.content
            else:
                result_text = str(response)

            if not result_text or len(result_text.strip()) == 0:
                result_text = "[Agent returned empty response]"

            all_results.append(result_text)

            click.secho(f"\n[Iteration {iteration} Result]:", fg="green")
            click.secho(result_text[:500] + ("..." if len(result_text) > 500 else ""), fg="white")

        except TimeoutError as e:
            click.secho(f"\n[Iteration {iteration} TIMEOUT]: {e}", fg="red", bold=True)
            result_text = f"[Iteration timed out after 60 seconds]"
            all_results.append(result_text)

        except Exception as e:
            click.secho(f"\n[Iteration {iteration} ERROR]: {e}", fg="red", bold=True)
            result_text = f"[Error during iteration: {str(e)}]"
            all_results.append(result_text)

    # Combine all results
    result_text = "\n\n=== EXPLORATION SUMMARY ===\n\n".join(
        [f"Step {i+1}:\n{r}" for i, r in enumerate(all_results)]
    )

    click.secho(f"\n[Debug] Total result length: {len(result_text)} chars", fg="magenta")

    # Store observation
    reward = calculate_reward(task, result_text)

    add_observation(
        agent_id=agent_id,
        episode_id=episode_id,
        observation_text=result_text,
        action_code="agent.run(objective)",
        outcome=result_text,
        reward=reward,
    )

    click.secho(f"\n[Explore] Result:", fg="green", bold=True)
    click.secho(result_text, fg="white")
    click.secho(f"\n[Explore] Episode complete! (Reward: {reward})", fg="green", bold=True)


@click.command()
@click.option(
    "--agent",
    "-a",
    type=click.Choice(list(AGENTS.keys())),
    required=True,
    help="Which explorer to send out"
)
@click.option(
    "--objective",
    "-o",
    default="Explore and learn about nature, animals, and the world around you",
    help="What the explorer should focus on"
)
@click.option(
    "--steps",
    "-s",
    default=DEFAULT_EPISODE_STEPS,
    help="How many exploration steps to take"
)
def explore(agent: str, objective: str, steps: int):
    """Send a curious explorer out to learn about the world using Agno"""

    click.secho("\n" + "="*60, fg="cyan")
    click.secho("Incubator - Exploration (Agno)", fg="cyan", bold=True)
    click.secho("="*60 + "\n", fg="cyan")

    run_agno_exploration(agent, objective, steps)


if __name__ == "__main__":
    explore()
