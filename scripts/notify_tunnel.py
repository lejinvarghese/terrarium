#!/usr/bin/env python3
"""Send tunnel URL notification to Telegram."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_notification(url: str, service_name: str = "Open WebUI"):
    """Send tunnel URL to Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env", file=sys.stderr)
        return

    try:
        import httpx

        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        # Service-specific emojis and descriptions
        service_info = {
            "Open WebUI": ("🌐", "Tap to open Open WebUI from anywhere!"),
            "Open Notebook": ("📓", "Tap to access your Open Notebook from anywhere!")
        }

        emoji, description = service_info.get(service_name, ("🌐", "Tap to access from anywhere!"))

        message = f"{emoji} *{service_name} Tunnel Active*\n\n{url}\n\n✅ {description}"

        response = httpx.post(
            api_url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=10.0,
        )

        if response.status_code == 200:
            print(f"✅ Telegram notification sent: {url}")
        else:
            print(f"⚠️  Failed to send notification: {response.status_code}", file=sys.stderr)

    except ImportError:
        print("⚠️  httpx not installed in main environment", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Error sending notification: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: notify_tunnel.py <tunnel_url> [service_name]", file=sys.stderr)
        sys.exit(1)

    tunnel_url = sys.argv[1]
    service_name = sys.argv[2] if len(sys.argv) > 2 else "Open WebUI"
    send_notification(tunnel_url, service_name)
