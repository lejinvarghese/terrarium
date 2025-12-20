#!/usr/bin/env python3
"""Test if incubator agents can use MCP tools"""

import asyncio
from agno.agent import Agent
from agno.models.ollama import Ollama
from src.core.tools import get_tools
from src.landscapes.undergrowth.incubator.config import MODEL_NAME


async def test_mcp_tools():
    """Test if agents can use actual MCP tools"""

    print("Loading MCP tools...")
    tools = get_tools()
    print(f"✓ Loaded {len(tools)} tool servers with {sum(len(t.functions) for t in tools)} total functions\n")

    # Create agent with simple, direct system prompt
    model = Ollama(id=MODEL_NAME)
    simple_agent = Agent(
        model=model,
        tools=tools,
        system_message="You are a helpful assistant. When asked to search or find information, USE YOUR TOOLS. Always call the appropriate tool function.",
        markdown=False,
        debug_mode=False,
    )

    print("=" * 60)
    print("TEST 1: arXiv search")
    print("=" * 60)
    response1 = await simple_agent.arun("Search arXiv for papers about quantum entanglement")
    print(f"\nResponse: {response1.content[:300] if hasattr(response1, 'content') else str(response1)[:300]}...")
    tool_count = len(response1.tools) if hasattr(response1, 'tools') and response1.tools else 0
    print(f"Tools used: {tool_count}")
    if tool_count > 0:
        print("✓ SUCCESS: Tool was called!")
    else:
        print("✗ FAILED: No tools called")

    print("\n" + "=" * 60)
    print("TEST 2: Tavily web search")
    print("=" * 60)
    response2 = await simple_agent.arun("Use tavily to search for latest news on AI breakthroughs")
    print(f"\nResponse: {response2.content[:300] if hasattr(response2, 'content') else str(response2)[:300]}...")
    tool_count2 = len(response2.tools) if hasattr(response2, 'tools') and response2.tools else 0
    print(f"Tools used: {tool_count2}")
    if tool_count2 > 0:
        print("✓ SUCCESS: Tool was called!")
    else:
        print("✗ FAILED: No tools called")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
