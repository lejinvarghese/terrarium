#!/usr/bin/env python3
"""Quick script to get your Telegram chat ID"""

import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


def _format_chat_info(chat) -> list[str]:
    """Format chat information as list of strings."""
    lines = [f"\nChat ID: {chat.id}", f"  Type: {chat.type}"]
    if chat.username:
        lines.append(f"  Username: @{chat.username}")
    if chat.first_name:
        lines.append(f"  Name: {chat.first_name} {chat.last_name or ''}")
    return lines


def _extract_unique_chats(updates):
    """Extract unique chat IDs from updates."""
    seen_chats = {}
    for update in updates:
        if update.message:
            chat = update.message.chat
            if chat.id not in seen_chats:
                seen_chats[chat.id] = chat
    return seen_chats


async def get_chat_id():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Error: TELEGRAM_TOKEN not found in .env")
        return

    bot = Bot(token=token)

    print("Fetching recent updates.")
    updates = await bot.get_updates()

    if not updates:
        print("\nNo recent messages found!")
        print("Send a message to your bot first, then run this script again.")
        return

    seen_chats = _extract_unique_chats(updates)

    if not seen_chats:
        print("\nNo messages found. Send a message to your bot first!")
        return

    print("\n=== Recent Chats ===")
    for chat in seen_chats.values():
        for line in _format_chat_info(chat):
            print(line)


if __name__ == "__main__":
    asyncio.run(get_chat_id())
