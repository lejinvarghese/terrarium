"""MCP tools configuration for Incubator agents"""

import asyncio
import os

import click
from agno.tools.mcp import MultiMCPTools

from src.landscapes.core.constants import NPM_DIRECTORY, ROOT_DIRECTORY

CUSTOM_MCP_SERVER_PATH = f"{ROOT_DIRECTORY}/mcp/server.py"


async def get_tools():
    """Initialize MCP tools. Caller is responsible for calling await tools.close() when done."""
    mcp_tools = MultiMCPTools(
        commands=[
            f"python3 {CUSTOM_MCP_SERVER_PATH}",
            "uv tool run arxiv-mcp-server --storage-path ./data/arxiv",
            f"{NPM_DIRECTORY}/tavily-mcp",
        ],
        env={**os.environ},
        timeout_seconds=120,
        allow_partial_failure=True,
        include_tools=[
            "generate_image",
            "scrape_recipe",
            "list_supported_recipe_sites",
            "search_papers",
            "download_paper",
            "list_papers",
            "read_paper",
            "tavily-search",
            "tavily-extract",
            "tavily-crawl",
            "tavily-map",
        ],
    )
    await mcp_tools.connect()
    return mcp_tools


def display_tools(tools, k: int = 40):
    """Display available MCP tools in a formatted way"""
    if tools:
        func_list = list(tools.functions)
        click.secho(f"Available tools ({len(func_list)}):", fg="yellow")
        for func in func_list[:k]:
            click.secho(f"- {func}", fg="blue")
        if len(func_list) > k:
            click.secho(f"... and {len(func_list) - k} more", fg="yellow")


async def main():
    """Example usage with proper cleanup."""
    tools = None
    try:
        tools = await get_tools()
        display_tools(tools)
    finally:
        if tools:
            click.secho("\nClosing connections.", fg="yellow")
            await tools.close()
            click.secho("✓ Cleanup complete", fg="green")


if __name__ == "__main__":
    asyncio.run(main())
