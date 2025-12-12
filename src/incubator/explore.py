#!/usr/bin/env python3
"""Exploration agent for Incubator - curious agents learning about the world"""

import os
import time
import click
from pathlib import Path

# Set memory management env vars before importing torch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from src.incubator.config import (
    MODEL_NAME,
    DEVICE,
    MAX_NEW_TOKENS,
    TEMPERATURE,
    DEFAULT_EPISODE_STEPS,
    USE_OLLAMA,
    OLLAMA_MODEL,
)
from src.incubator.agents import get_agent_config, AGENTS
from src.incubator.models import add_observation
from src.incubator.tools import get_tools


def calculate_reward(action: str, outcome: str) -> float:
    """Calculate reward for an observation.

    Simple heuristic:
    - Successful actions (no errors) get positive reward
    - Actions with errors or failures get negative reward
    - Actions that discover new information get higher reward
    """
    outcome_lower = outcome.lower()

    # Negative indicators
    if any(x in outcome_lower for x in ["error", "failed", "exception", "could not"]):
        return -0.3

    # Neutral/learning
    if any(x in outcome_lower for x in ["found", "discovered", "learned"]):
        return 0.7

    # Positive default
    return 0.5


def run_model_exploration(
    agent_id: str,
    objective: str,
    steps: int = DEFAULT_EPISODE_STEPS
):
    """Run exploration with model + agent"""

    click.secho(f"\n[Explore] Loading model...", fg="cyan", bold=True)

    from smolagents import ToolCallingAgent, LiteLLMModel, ToolCollection
    from mcp import StdioServerParameters

    # Get agent configuration
    agent_config = get_agent_config(agent_id)

    # Get base tools
    base_tools = get_tools()

    if USE_OLLAMA:
        # Use Ollama with SmolVLM as intended
        click.secho(f"[Explore] Using Ollama model: {OLLAMA_MODEL}", fg="yellow")
        click.secho(f"[Explore] Ollama handles CPU/GPU offloading automatically", fg="cyan")

        model = LiteLLMModel(
            model_id=f"ollama/{OLLAMA_MODEL}",
            max_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
        )

        click.secho(f"[Explore] Model ready!", fg="green")

    else:
        # Fallback to TransformersModel with quantization
        from smolagents import TransformersModel
        from transformers import BitsAndBytesConfig

        click.secho(f"[Explore] Model: {MODEL_NAME}", fg="yellow")
        click.secho(f"[Explore] Loading with 4-bit quantization...", fg="cyan")

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype="float16",
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        model = TransformersModel(
            model_id=MODEL_NAME,
            max_new_tokens=MAX_NEW_TOKENS,
            device_map="auto",
            model_kwargs={"quantization_config": quantization_config},
        )

        click.secho(f"[Explore] Model loaded!", fg="green")

    click.secho(f"\n[Explore] Loading MCP servers...", fg="cyan")

    # Get the path to the Terrarium MCP server
    project_root = Path(__file__).parent.parent.parent
    mcp_server_path = project_root / "src" / "mcp" / "server.py"

    # Configure MCP servers
    mcp_servers = {
        "terrarium": StdioServerParameters(
            command="python",
            args=[str(mcp_server_path)],
            env={**os.environ},
        ),
        "arxiv": StdioServerParameters(
            command="uv",
            args=[
                "tool",
                "run",
                "arxiv-mcp-server",
                "--storage-path",
                str(Path.home() / ".arxiv-mcp-server" / "papers")
            ],
            env={**os.environ},
        ),
        "tavily": StdioServerParameters(
            command="/home/starscream/.npm-global/bin/tavily-mcp",
            args=[],
            env={**os.environ},
        ),
        "spotify": StdioServerParameters(
            command="/home/starscream/.npm-global/bin/spotify-mcp",
            args=[],
            env={**os.environ},
        ),
    }

    click.secho(f"[Explore] Creating {agent_config['name']}...", fg="cyan")

    # Load tools from all MCP servers and combine with base tools
    all_mcp_tools = []
    base_tool_names = {tool.name for tool in base_tools}

    # Load each MCP server's tools
    for server_name, server_params in mcp_servers.items():
        try:
            click.secho(f"[Explore] Loading {server_name}...", fg="yellow")
            with ToolCollection.from_mcp(server_params, trust_remote_code=True) as mcp_collection:
                # Filter out duplicate tool names
                unique_tools = [
                    tool for tool in mcp_collection.tools
                    if tool.name not in base_tool_names and tool.name not in {t.name for t in all_mcp_tools}
                ]
                all_mcp_tools.extend(unique_tools)
                click.secho(f"[Explore]   ✓ {server_name}: {len(unique_tools)} tools", fg="green")
        except Exception as e:
            click.secho(f"[Explore]   ✗ {server_name}: {e}", fg="red")
            continue

    all_tools = [*base_tools, *all_mcp_tools]

    # Build list of tool names for display and guidance
    tool_names = [tool.name for tool in all_tools]

    click.secho(f"\n[Explore] Loaded {len(all_mcp_tools)} unique tools from MCP servers", fg="green", bold=True)
    click.secho(f"[Explore] Total tools available: {len(all_tools)}", fg="cyan", bold=True)

    # Debug: Show available tool names
    click.secho(f"\n[Explore] Available tool names:", fg="yellow")
    for i, name in enumerate(sorted(tool_names)[:20], 1):
        click.secho(f"  {i}. {name}", fg="white")
    if len(tool_names) > 20:
        click.secho(f"  ... and {len(tool_names) - 20} more", fg="white", dim=True)

    # Use ToolCallingAgent with combined tools
    agent = ToolCallingAgent(
        tools=all_tools,
        model=model,
        max_steps=steps,
    )

    # Run exploration with persona context
    episode_id = f"{agent_id}_{int(time.time())}"
    click.secho(f"[Explore] Episode: {episode_id}\n", fg="cyan")

    # Prepend system prompt and tool guidance to objective
    exploration_guidance = f"""
{agent_config['system_prompt']}

AVAILABLE TOOLS: {', '.join(sorted(tool_names[:20]))}... and {len(tool_names) - 20} more

YOUR OBJECTIVE: {objective}

Use the tools available to explore, learn, and gather information about your objective.
"""

    result = agent.run(exploration_guidance)

    # Store observation
    reward = calculate_reward(str(result), str(result))

    add_observation(
        agent_id=agent_id,
        episode_id=episode_id,
        observation_text=str(result),
        action_code="agent.run(objective)",
        outcome=str(result),
        reward=reward,
    )

    click.secho(f"\n[Explore] Episode complete!", fg="green", bold=True)


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
    """Send a curious explorer out to learn about the world"""

    click.secho("\n" + "="*60, fg="cyan")
    click.secho("Incubator - Exploration", fg="cyan", bold=True)
    click.secho("="*60 + "\n", fg="cyan")

    run_model_exploration(agent, objective, steps)


if __name__ == "__main__":
    explore()
