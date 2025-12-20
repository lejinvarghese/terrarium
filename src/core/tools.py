"""MCP tools configuration for Incubator agents"""

import os
import asyncio
import click
from pathlib import Path


async def _initialize_tools():
    """Async helper to initialize MCP tools with proper connection"""
    from agno.tools.mcp import MCPTools
    from mcp import StdioServerParameters

    project_root = Path(__file__).parent.parent.parent

    mcp_configs = {
        "terrarium": {
            "command": "python3",
            "args": [str(project_root / "src" / "mcp" / "server.py")],
        },
        "arxiv": {
            "command": "uv",
            "args": [
                "tool",
                "run",
                "arxiv-mcp-server",
                "--storage-path",
                str(Path.home() / ".arxiv-mcp-server" / "papers"),
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

    tools = []
    for server_name, config in mcp_configs.items():
        try:
            click.secho(f"[Tools] Loading {server_name}...", fg="yellow", dim=True)

            server_params = StdioServerParameters(
                command=config["command"], args=config["args"], env={**os.environ}
            )

            mcp_tools = MCPTools(
                server_params=server_params,
                tool_name_prefix=f"{server_name}_",
                timeout_seconds=120,
            )

            # CRITICAL: Connect and initialize to discover tools
            await mcp_tools.connect()
            await mcp_tools.initialize()

            tool_count = len(mcp_tools.functions)
            if tool_count > 0:
                tools.append(mcp_tools)
                click.secho(f"[Tools]   ✓ {server_name}: {tool_count} tools", fg="green")
            else:
                click.secho(f"[Tools]   ⚠ {server_name}: no tools found", fg="yellow")

        except Exception as e:
            click.secho(f"[Tools]   ✗ {server_name}: {e}", fg="red")
            continue

    return tools


def get_tools():
    """Initialize and return tools for agent use."""
    # Run async initialization in event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create new task
            import nest_asyncio
            nest_asyncio.apply()
        return loop.run_until_complete(_initialize_tools())
    except RuntimeError:
        # No event loop exists, create one
        return asyncio.run(_initialize_tools())
