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
GIRLFRIEND_TELEGRAM_CHAT_ID = os.getenv("GIRLFRIEND_TELEGRAM_CHAT_ID")

def send_notification(url: str, service_name: str = "Open WebUI"):
    """Send tunnel URL to Telegram (both you and girlfriend)."""
    if not TELEGRAM_TOKEN:
        print("⚠️  Missing TELEGRAM_TOKEN in .env", file=sys.stderr)
        return

    # Collect all chat IDs to send to
    chat_ids = []
    if TELEGRAM_CHAT_ID:
        chat_ids.append(TELEGRAM_CHAT_ID)
    if GIRLFRIEND_TELEGRAM_CHAT_ID:
        chat_ids.append(GIRLFRIEND_TELEGRAM_CHAT_ID)

    if not chat_ids:
        print("⚠️  No chat IDs configured in .env", file=sys.stderr)
        return

    try:
        import httpx

        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        # Service-specific emojis and descriptions
        service_info = {
            "Dome": ("🌐✨", "Your Dome is glowing - accessible from anywhere in the world"),
            "Archive": ("📚🔍", "Your Archive awaits - knowledge flows through any connection")
        }

        emoji, description = service_info.get(service_name, ("🌐", "Portal active - reach from anywhere"))

        message = f"{emoji} *{service_name}* is live\n\n🔗 {url}\n\n{description}"

        # Send to all configured chat IDs
        for chat_id in chat_ids:
            response = httpx.post(
                api_url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
                timeout=10.0,
            )

            if response.status_code != 200:
                print(f"⚠️  Telegram notification failed for {chat_id}: {response.status_code}", file=sys.stderr)

    except ImportError:
        print("⚠️  httpx not installed in main environment", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Error sending notification: {e}", file=sys.stderr)

def send_combined_notification(portals: list[tuple[str, str]]):
    """Send combined tunnel URLs to Telegram (both you and girlfriend).

    Args:
        portals: List of (service_name, url) tuples
    """
    if not TELEGRAM_TOKEN:
        return

    # Collect all chat IDs to send to
    chat_ids = []
    if TELEGRAM_CHAT_ID:
        chat_ids.append(TELEGRAM_CHAT_ID)
    if GIRLFRIEND_TELEGRAM_CHAT_ID:
        chat_ids.append(GIRLFRIEND_TELEGRAM_CHAT_ID)

    if not chat_ids:
        return

    try:
        import httpx

        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        # Build message with all portals
        lines = ["🌿 *Terrarium Portals Active*\n"]

        for name, url in portals:
            emoji = "🌐✨" if name == "Dome" else "📚🔍"
            lines.append(f"{emoji} [{name}]({url})\n")

        lines.append("✨ All systems online.")

        message = "\n".join(lines)

        # Send to all configured chat IDs
        for chat_id in chat_ids:
            response = httpx.post(
                api_url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
                timeout=10.0,
            )

            if response.status_code != 200:
                print(f"⚠️  Telegram notification failed for {chat_id}: {response.status_code}", file=sys.stderr)

    except ImportError:
        pass  # Silently fail if httpx not installed
    except Exception:
        pass  # Silently fail on any error

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: notify_tunnel.py <tunnel_url> [service_name]", file=sys.stderr)
        print("       notify_tunnel.py --combined <name1> <url1> <name2> <url2> .", file=sys.stderr)
        sys.exit(1)

    # Check for combined mode
    if sys.argv[1] == "--combined":
        # Parse name/url pairs
        args = sys.argv[2:]
        if len(args) % 2 != 0:
            print("Error: --combined requires name/url pairs", file=sys.stderr)
            sys.exit(1)

        portals = [(args[i], args[i+1]) for i in range(0, len(args), 2)]
        send_combined_notification(portals)
    else:
        # Single notification mode
        tunnel_url = sys.argv[1]
        service_name = sys.argv[2] if len(sys.argv) > 2 else "Open WebUI"
        send_notification(tunnel_url, service_name)
