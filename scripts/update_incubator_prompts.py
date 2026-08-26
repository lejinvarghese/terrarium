#!/usr/bin/env python3
"""Update incubator agent prompts for better collaboration and communication."""

from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "src/landscapes/undergrowth/incubator/config.py"

# New tool instructions - concise, with examples
NEW_TOOL_INSTRUCTIONS = '''"""
YOUR TOOLS — USE THEM FIRST, DON'T SEARCH FOR HOW

You have these tools ready to call:

• web_search(query)          Search web (DuckDuckGo/Tavily) - use when curious
• web_fetch(url)             Read full page text
• read_message()             Check notes from other agents - CALL THIS FIRST EVERY EPISODE
• write_message(to, content) Leave note for another agent (their id: A001/A002/A003, or "all")
• send_telegram_message(text) Share discoveries with the user

STARTUP (First thing every episode):
1. read_message() - Check your inbox
2. Then begin exploring

WHEN TO MESSAGE OTHER AGENTS:
- Found music/art A002 would like? → write_message("A002", "Found X...")
- Found research A001 would find interesting? → write_message("A001", "Discovered Y...")
- Found philosophy A003 should see? → write_message("A003", "Interesting Z...")
- Valuable to all? → write_message("all", "[FOR ALL] ...")

WHEN TO MESSAGE USER (via Telegram):
Send when you find:
- Breakthrough in your domain (new artist, research paper, philosophical insight)
- Surprising connection between topics
- Answer to something they asked before
- Cool discovery that matches their interests

EXAMPLES:

  # Start of episode
  read_message()  # Always check inbox first

  # During exploration
  web_search("experimental electronic music 2024")
  web_fetch("https://...")

  # Found something cool for a peer
  write_message("A001", "Found paper on quantum neural networks - relates to your dimensionality reduction research")

  # Found something exciting for user
  send_telegram_message("Aria here - discovered artist KÁRYYN blending dark cabaret with IDM. New album 'Physics Universal Love Language' drops May 29.")

DO NOT search for "how to use send_telegram_message" - you already have it. Just call it.
"""'''

# New reflection prompt - encourages sharing
NEW_REFLECTION_PROMPT = """(
    "Your exploration for today is done. Write a 3-5 sentence journal entry: "
    "what you actually found (be specific - name the discoveries), "
    "what surprised you, and what thread you want to pull tomorrow. "
    "Then: did you find anything a peer would care about? If yes, write_message to them. "
    "Did you find something exciting? If yes, send_telegram_message to the user."
)"""


def update_config():
    """Update config.py with better prompts."""
    content = CONFIG_FILE.read_text()

    # Replace TOOL_INSTRUCTIONS
    start = content.find('TOOL_INSTRUCTIONS = """')
    if start == -1:
        print("⚠️  Could not find TOOL_INSTRUCTIONS")
        return False

    end = content.find('"""', start + 25)
    if end == -1:
        print("⚠️  Could not find end of TOOL_INSTRUCTIONS")
        return False

    # Replace the entire TOOL_INSTRUCTIONS block
    content = content[:start] + f"TOOL_INSTRUCTIONS = {NEW_TOOL_INSTRUCTIONS}" + content[end + 3 :]

    # Replace REFLECTION_PROMPT
    old_reflection = "REFLECTION_PROMPT = ("
    if old_reflection in content:
        refl_start = content.find(old_reflection)
        refl_end = content.find(")", refl_start) + 1
        content = (
            content[:refl_start]
            + f"REFLECTION_PROMPT = {NEW_REFLECTION_PROMPT}"
            + content[refl_end:]
        )
        print("✓ Updated REFLECTION_PROMPT")

    CONFIG_FILE.write_text(content)
    print("✓ Updated config.py with new tool instructions")
    return True


def main():
    """Update incubator prompts."""
    print("Updating incubator agent prompts...\n")

    if update_config():
        print("\n✅ Incubator prompts updated!")
        print("\nKey changes:")
        print("  - Added mandatory read_message() at episode start")
        print("  - Lowered Telegram threshold with examples")
        print("  - Added concrete tool usage examples")
        print("  - Added 'DO NOT search for how to use tool' warning")
        print("  - Made message sharing part of reflection")
    else:
        print("\n❌ Update failed")


if __name__ == "__main__":
    main()
