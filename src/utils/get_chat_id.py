#!/usr/bin/env python3
"""Quick script to get your Telegram chat ID"""

import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def get_chat_id():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Error: TELEGRAM_TOKEN not found in .env")
        return

    bot = Bot(token=token)

    print("Fetching recent updates...")
    updates = await bot.get_updates()

    if not updates:
        print("\nNo recent messages found!")
        print("Send a message to your bot first, then run this script again.")
        return

    print("\n=== Recent Chats ===")
    seen_chats = set()
    for update in updates:
        if update.message:
            chat = update.message.chat
            if chat.id not in seen_chats:
                seen_chats.add(chat.id)
                print(f"\nChat ID: {chat.id}")
                print(f"  Type: {chat.type}")
                if chat.username:
                    print(f"  Username: @{chat.username}")
                if chat.first_name:
                    print(f"  Name: {chat.first_name} {chat.last_name or ''}")

    if not seen_chats:
        print("\nNo messages found. Send a message to your bot first!")

if __name__ == "__main__":
    asyncio.run(get_chat_id())
