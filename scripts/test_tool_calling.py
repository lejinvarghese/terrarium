#!/usr/bin/env python3
"""Test if qwen3:1.7b can actually use tools with Agno"""

import asyncio
from agno.agent import Agent
from agno.models.ollama import Ollama


def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city

    Returns:
        A weather description
    """
    print(f"[TOOL CALLED] get_weather(city='{city}')")
    return f"The weather in {city} is sunny and 72°F"


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    print(f"[TOOL CALLED] add_numbers(a={a}, b={b})")
    return a + b


async def test_tool_calling():
    """Test if the model can use simple tools"""

    # Create agent with tools (just pass functions directly)
    model = Ollama(id="qwen3:1.7b")
    agent = Agent(
        model=model,
        tools=[get_weather, add_numbers],  # Pass functions directly
        markdown=False,
        debug_mode=False,  # Set to False for cleaner output
    )

    print("=" * 60)
    print("TEST 1: Math Tool")
    print("=" * 60)
    response1 = await agent.arun("What is 15 plus 27?")
    print(f"\nResponse: {response1.content if hasattr(response1, 'content') else response1}")
    print(f"Tools used: {len(response1.tools) if hasattr(response1, 'tools') and response1.tools else 0} tools")

    print("\n" + "=" * 60)
    print("TEST 2: Weather Tool")
    print("=" * 60)
    response2 = await agent.arun("What's the weather like in Paris?")
    print(f"\nResponse: {response2.content if hasattr(response2, 'content') else response2}")
    print(f"Tools used: {len(response2.tools) if hasattr(response2, 'tools') and response2.tools else 0} tools")

    print("\n" + "=" * 60)
    print("TEST 3: Explicit Tool Request")
    print("=" * 60)
    response3 = await agent.arun("Use the get_weather function to check Tokyo's weather")
    print(f"\nResponse: {response3.content if hasattr(response3, 'content') else response3}")
    print(f"Tools used: {len(response3.tools) if hasattr(response3, 'tools') and response3.tools else 0} tools")


if __name__ == "__main__":
    asyncio.run(test_tool_calling())
