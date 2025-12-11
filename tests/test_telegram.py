#!/usr/bin/env python3
"""Test script for Telegram messaging"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Simple test using the MCP tool directly
async def test_telegram():
    from src.mcp.server import send_telegram_message

    result = await send_telegram_message("🤖 Test message from Terrarium MCP!")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_telegram())
