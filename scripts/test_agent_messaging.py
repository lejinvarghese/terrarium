#!/usr/bin/env python3
"""Test inter-agent messaging system"""

import asyncio

from src.mcp.server import get_my_messages, send_agent_message


async def test_messaging():
    print("=" * 60)
    print("TESTING INTER-AGENT MESSAGING SYSTEM")
    print("=" * 60)

    # Test 1: Send a message from Cassia to Nigella
    print("\n📤 Test 1: Cassia → Nigella (delegation)")
    result = await send_agent_message(
        to_agent="nigella",
        content="User wants high-protein Italian dinner ideas for tonight",
        from_agent="cassia",
        message_type="delegation",
    )
    print(f"  Status: {result.get('status')}")
    print(f"  From: {result.get('from')} → To: {result.get('to')}")

    # Test 2: Send a message from Nyx to Sage
    print("\n📤 Test 2: Nyx → Sage (note)")
    result = await send_agent_message(
        to_agent="sage",
        content="Found breakthrough paper on quantum computing at room temperature",
        from_agent="nyx",
        message_type="note",
    )
    print(f"  Status: {result.get('status')}")
    print(f"  From: {result.get('from')} → To: {result.get('to')}")

    # Test 3: Send a message from Freya to Cassia
    print("\n📤 Test 3: Freya → Cassia (update)")
    result = await send_agent_message(
        to_agent="cassia",
        content="User's gym session should be scheduled post-5pm for optimal recovery",
        from_agent="freya",
        message_type="update",
    )
    print(f"  Status: {result.get('status')}")
    print(f"  From: {result.get('from')} → To: {result.get('to')}")

    # Test 4: Check Nigella's messages
    print("\n📬 Test 4: Checking Nigella's inbox")
    messages = await get_my_messages(agent_id="nigella", limit=5)
    print(f"  Message count: {messages.get('message_count')}")
    if messages.get("messages"):
        for i, msg in enumerate(messages["messages"][:3], 1):
            print(f"  [{i}] {msg.get('memory', '')[:80]}...")

    # Test 5: Check Sage's messages
    print("\n📬 Test 5: Checking Sage's inbox")
    messages = await get_my_messages(agent_id="sage", limit=5)
    print(f"  Message count: {messages.get('message_count')}")
    if messages.get("messages"):
        for i, msg in enumerate(messages["messages"][:3], 1):
            print(f"  [{i}] {msg.get('memory', '')[:80]}...")

    # Test 6: Check Cassia's messages
    print("\n📬 Test 6: Checking Cassia's inbox")
    messages = await get_my_messages(agent_id="cassia", limit=5)
    print(f"  Message count: {messages.get('message_count')}")
    if messages.get("messages"):
        for i, msg in enumerate(messages["messages"][:3], 1):
            print(f"  [{i}] {msg.get('memory', '')[:80]}...")

    print("\n✅ Messaging system test complete!")


if __name__ == "__main__":
    asyncio.run(test_messaging())
