#!/usr/bin/env python3
"""Test script for persona-based Telegram messages"""

import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PERSONA_EMOJIS = {
    "anya": "🎨",
    "cassia": "☀️",
    "freya": "💪",
    "nigella": "🍷",
    "nyx": "🚀",
    "sage": "📚",
    "system": "🌿",
}

async def send_message(message: str, persona: str):
    """Send a test message with persona"""
    bot = Bot(token=TELEGRAM_TOKEN)
    emoji = PERSONA_EMOJIS.get(persona.lower(), "🤖")
    formatted_message = f"{emoji} *{persona.title()}*\n{message}"

    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=formatted_message,
        parse_mode="Markdown"
    )

async def test_personas():
    """Send test messages for each persona"""
    personas = [
        ("anya", "Your evening playlist 'Moonlit Walk' is ready - dark ambient with a touch of haunting vocals."),
        ("cassia", "Good morning! 🌤️ Clear skies today, 18°C. You have meetings at 10am and 2pm. Gym at 6?"),
        ("freya", "Great session yesterday! Your progressive overload is on track. Consider adding 2.5kg to bench today."),
        ("nigella", "Tonight's special: Butternut squash risotto with sage - squash is at peak season right now. Pair with a crisp Pinot Grigio."),
        ("nyx", "New paper on neural scaling laws just dropped. Exponential compute trends continue - we're ahead of schedule."),
        ("sage", "That Gene Wolfe novel pairs perfectly with your current systems thinking phase. Adding to your queue."),
        ("system", "Terrarium services are online. All bots connected."),
    ]

    for persona, message in personas:
        await send_message(message, persona)
        print(f"✓ {persona.title()}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_personas())
