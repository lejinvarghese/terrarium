#!/usr/bin/env python3
"""
Inspection script to reveal the inner workings of the Incubator agents.
Uses click.secho for consistent project styling.
"""

import sys
from pathlib import Path

import click

# Ensure src is in the python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.landscapes.undergrowth.incubator.agents import agent_registry


def inspect_system():
    click.secho("\n" + "=" * 60, fg="cyan", bold=True)
    click.secho("🔍 INCUBATOR SYSTEM INSPECTION", fg="cyan", bold=True)
    click.secho("=" * 60, fg="cyan", bold=True)

    # 1. System Prompt Analysis
    agent_id = "A001"
    click.secho(f"\n[1] SYSTEM PROMPT (Agent {agent_id})", fg="yellow", bold=True)
    click.secho("-" * 60, fg="yellow")

    try:
        agent = agent_registry.get(agent_id)
        # Split by lines to apply formatting if needed, or just print dim
        click.secho(agent.system_prompt, fg="white", dim=True)
    except Exception as e:
        click.secho(f"Error loading agent: {e}", fg="red", bold=True)

    # 2. Memory Configuration
    click.secho("\n[2] MEMORY CONFIGURATION", fg="yellow", bold=True)
    click.secho("-" * 60, fg="yellow")

    click.secho("Memory Database: ", nl=False, fg="white")
    click.secho("SQLite", fg="green")

    click.secho("Memory Persistence: ", nl=False, fg="white")
    click.secho("ENABLED", fg="green", bold=True)

    click.secho("Context Loading:    ", nl=False, fg="white")
    click.secho("ENABLED (add_memories_to_context=True)", fg="green")

    click.secho("DB Path:            ", nl=False, fg="white")
    click.secho("src/landscapes/undergrowth/incubator/memory.db", fg="cyan")

    # 3. Tool Configuration
    click.secho("\n[3] ACTIVE TOOLS (MCP)", fg="yellow", bold=True)
    click.secho("-" * 60, fg="yellow")

    try:
        import inspect
        import re

        import src.core.tools as tools_module

        source = inspect.getsource(tools_module.get_tools)
        mcp_configs = re.findall(r'"(\w+)":\s*{', source)

        if mcp_configs:
            click.secho("Detected MCP Servers configured in src/core/tools.py:", fg="white")
            for tool in mcp_configs:
                click.secho(f"  • {tool}", fg="magenta", bold=True)
        else:
            click.secho("Could not parse tools from source automatically.", fg="red")
            click.secho("Please check src/core/tools.py directly.", fg="white", dim=True)
    except Exception as e:
        click.secho(f"Error inspecting tools: {e}", fg="red")

    click.secho("\n" + "=" * 60, fg="cyan", bold=True)
    click.secho("✓ Inspection Complete", fg="green", bold=True)
    click.secho("=" * 60 + "\n", fg="cyan", bold=True)


if __name__ == "__main__":
    inspect_system()
