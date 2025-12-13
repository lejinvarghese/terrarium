"""MCP tools configuration for Incubator agents"""

import os
import click
from pathlib import Path


def get_tools():
    """Initialize and return tools for agent use."""
    from agno.tools.mcp import MCPTools
    from mcp import StdioServerParameters

    project_root = Path(__file__).parent.parent.parent

    mcp_configs = {
        "terrarium": {
            "command": "python",
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
            click.secho(f"[Tools] Loading {server_name}...", fg="yellow")

            server_params = StdioServerParameters(
                command=config["command"], args=config["args"], env={**os.environ}
            )

            mcp_tools = MCPTools(
                server_params=server_params,
                tool_name_prefix=f"{server_name}_",
                timeout_seconds=120,
            )
            tools.append(mcp_tools)
            click.secho(f"[Tools]   ✓ {server_name} loaded", fg="green")
        except Exception as e:
            click.secho(f"[Tools]   ✗ {server_name}: {e}", fg="red")
            continue

    return tools
