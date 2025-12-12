"""Simple tools for Incubator agents to explore and learn"""

import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict
import click
from smolagents import tool



@tool
def read_memory(query: str, limit: int = 5) -> List[str]:
    """Search Terrarium's memory to learn from past conversations.

    Args:
        query: What memory to search for
        limit: How many memories to retrieve

    Returns:
        List of relevant memories
    """
    click.secho(f"[Tool] Searching memory for: {query}", fg="blue")

    try:
        from src.engine.memory_config import get_memory, USER_ID
        memory = get_memory()
        results = memory.search(query, limit=limit, user_id=USER_ID)

        # Handle different result formats
        if not results:
            return []

        # Results can be dicts, strings, or other formats
        formatted = []
        for r in results:
            if isinstance(r, dict):
                formatted.append(r.get("memory", str(r)))
            else:
                formatted.append(str(r))
        return formatted

    except Exception as e:
        click.secho(f"[Tool] Memory search failed: {e}", fg="red")
        return []


@tool
def check_services() -> Dict[str, bool]:
    """Check which Terrarium services are running.

    Returns:
        Dictionary of service names and their status
    """
    click.secho("[Tool] Checking Terrarium services...", fg="blue")

    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            services = result.stdout.strip().split("\n")
            return {service: True for service in services if service}
        else:
            return {}
    except Exception as e:
        click.secho(f"[Tool] Service check failed: {e}", fg="red")
        return {}


@tool
def read_logs(service: str, lines: int = 30) -> str:
    """Read recent logs from a Terrarium service.

    Args:
        service: Name of the service (dome, engine, portal, etc.)
        lines: How many lines to read

    Returns:
        Log content as text
    """
    click.secho(f"[Tool] Reading {lines} lines from {service} logs...", fg="blue")

    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", service, "-S", f"-{lines}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"[Could not read logs from {service}]"
    except Exception as e:
        click.secho(f"[Tool] Log reading failed: {e}", fg="red")
        return f"[Error reading logs: {e}]"


@tool
def take_screenshot(url: str) -> str:
    """Take a screenshot of a web page to see what it looks like.

    Args:
        url: The web address to capture

    Returns:
        Path to the saved screenshot
    """
    click.secho(f"[Tool] Taking screenshot of: {url}", fg="blue")

    try:
        from playwright.sync_api import sync_playwright
        from .config import SCREENSHOT_DIR

        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.screenshot(path=str(filepath))
            browser.close()

        click.secho(f"[Tool] Screenshot saved: {filepath}", fg="green")
        return str(filepath)

    except Exception as e:
        click.secho(f"[Tool] Screenshot failed: {e}", fg="red")
        return f"[Could not capture screenshot: {e}]"


@tool
def get_schedule() -> Dict:
    """See what tasks are scheduled in Terrarium.

    Returns:
        Dictionary of scheduled tasks
    """
    click.secho("[Tool] Loading scheduled tasks...", fg="blue")

    try:
        schedule_path = Path(__file__).parent.parent / "configs" / "schedule.json"

        if schedule_path.exists():
            with open(schedule_path) as f:
                schedule = json.load(f)
            return schedule
        else:
            return {"error": "Schedule file not found"}
    except Exception as e:
        click.secho(f"[Tool] Schedule loading failed: {e}", fg="red")
        return {"error": str(e)}


@tool
def list_bots() -> List[Dict[str, str]]:
    """See what bots live in the Terrarium.

    Returns:
        List of bot names and their descriptions
    """
    click.secho("[Tool] Discovering Terrarium bots...", fg="blue")

    try:
        bots_dir = Path(__file__).parent.parent / "bots"
        bots = []

        if bots_dir.exists():
            for bot_file in bots_dir.glob("*.md"):
                with open(bot_file) as f:
                    content = f.read()
                    # Extract first line as description
                    lines = content.strip().split("\n")
                    description = lines[1] if len(lines) > 1 else "A Terrarium bot"

                bots.append({
                    "name": bot_file.stem,
                    "description": description[:200]
                })

        return bots
    except Exception as e:
        click.secho(f"[Tool] Bot discovery failed: {e}", fg="red")
        return []


# Tool registry for easy access
TERRARIUM_TOOLS = [
    read_memory,
    check_services,
    read_logs,
    get_schedule,
    list_bots,
]


def get_tools():
    """Get all available tools as a list"""
    return TERRARIUM_TOOLS


def get_tools_dict():
    """Get tools as a dictionary for simple mode"""
    return {
        "read_memory": read_memory,
        "check_services": check_services,
        "read_logs": read_logs,
        "get_schedule": get_schedule,
        "list_bots": list_bots,
    }


if __name__ == "__main__":
    # Test tools
    click.secho("\n[Incubator] Testing tools...\n", fg="cyan", bold=True)

    click.secho("Testing check_services:", fg="yellow")
    services = check_services()
    click.secho(f"  Found services: {list(services.keys())}\n", fg="white")

    click.secho("Testing get_schedule:", fg="yellow")
    schedule = get_schedule()
    click.secho(f"  Tasks: {len(schedule.get('tasks', []))}\n", fg="white")

    click.secho("Testing list_bots:", fg="yellow")
    bots = list_bots()
    click.secho(f"  Bots: {[b['name'] for b in bots]}\n", fg="white")
