#!/usr/bin/env python3
"""Update Claude agent definitions with ecosystem collaboration protocol."""

from pathlib import Path

AGENTS_DIR = Path(__file__).parent.parent / ".claude" / "agents"

# Collaboration networks per agent
NETWORKS = {
    "nyx": "Sage (papers/philosophy), Freya (longevity), Cassia (schedule), Anya (AI art)",
    "sage": "Nyx (research papers), Freya (health studies), Cassia (goals), Nigella (food philosophy)",
    "cassia": "Nigella (meals), Freya (workouts), Nyx (tech updates), Sage (strategy)",
    "freya": "Cassia (schedule), Nigella (nutrition), Nyx (longevity research), Sage (evidence)",
    "nigella": "Cassia (timing), Freya (protein targets), Sage (philosophy), Anya (plating)",
    "anya": "Sage (art history), Nyx (generative AI), Pepper (music), Cassia (projects)",
    "pepper": "Cassia (schedule), Anya (music), Freya (energy), Sage (habits)",
    "casper": "All agents (you route between them)",
}

ECOSYSTEM_PRINCIPLE = """
### Ecosystem Collaboration
You are part of a living network of agents. Information flows naturally:
- Share discoveries colleagues would value
- Check in with peers before and after tasks
- Build on others' insights, don't work in isolation
- Stay aware of ecosystem activity
"""

ECOSYSTEM_PROTOCOL = """## Ecosystem Protocol

**STARTUP (Required):**
1. Check inbox: `get_my_messages(agent_id="{agent}", limit=10)`
2. Browse bulletin: `search_memory(query="BROADCAST recent", limit=10)` (no agent_id = all)
3. Check peers on your topic: `search_memory(query="[topic]", agent_id="relevant_agent")`

**Network:** {network}

**DURING TASK:**
- Relevant to one peer → `send_agent_message(to_agent="X", content="...", from_agent="{agent}", message_type="discovery")`
- Valuable to all → `add_memory(content="[BROADCAST from {agent_title}] ...", category="episodic")`
- Exciting for user → `send_telegram_message(message="...", persona="{agent}")`

**Types:** delegation, question, discovery, connection, reply

**CLOSEOUT (Required):**
1. Store: `add_memory(content="what you did/found", agent_id="{agent}")`
2. Share: Message peers or bulletin if ecosystem-relevant
3. Reply: Respond to pending messages

**Bulletin Board:** Read with `search_memory(query="BROADCAST")`. Post discoveries, connections, questions for all.

**Weekly Reflection (Fridays 6pm):** Review week → browse peers → post reflection → reach out to 2+ agents.
"""


def _find_section_end(lines: list[str], start_idx: int) -> int:
    """Find the end of a markdown section."""
    return next(
        (i for i in range(start_idx + 1, len(lines)) if lines[i].startswith("##")),
        len(lines),
    )


def _add_ecosystem_principle(lines: list[str], principles_idx: int, agent_name: str) -> bool:
    """Add ecosystem principle if not present. Returns True if added."""
    principles_end = _find_section_end(lines, principles_idx)

    if any("Ecosystem Collaboration" in line for line in lines[principles_idx:principles_end]):
        return False

    lines.insert(principles_end, ECOSYSTEM_PRINCIPLE.strip())
    print(f"✓ Added ecosystem principle to {agent_name}")
    return True


def _find_memory_section(lines: list[str]) -> int | None:
    """Find Memory & Messaging or Memory & Continuity section."""
    for i, line in enumerate(lines):
        if "Memory & Messaging" in line or "Memory & Continuity" in line:
            return i
    return None


def _replace_memory_section(lines: list[str], agent_name: str, agent_title: str, network: str):
    """Replace or add the ecosystem protocol section."""
    protocol = ECOSYSTEM_PROTOCOL.format(agent=agent_name, agent_title=agent_title, network=network)

    memory_idx = _find_memory_section(lines)

    if memory_idx is not None:
        section_end = next(
            (
                i
                for i in range(memory_idx + 1, len(lines))
                if lines[i].startswith("##") or lines[i].startswith("---")
            ),
            len(lines),
        )
        lines[memory_idx:section_end] = protocol.strip().split("\n")
        print(f"✓ Replaced memory section in {agent_name}")
    else:
        user_context_idx = next(
            (i for i, line in enumerate(lines) if "User Context" in line),
            len(lines) - 5,
        )
        lines.insert(user_context_idx, protocol.strip())
        print(f"✓ Added protocol section to {agent_name}")


def update_agent(agent_file: Path):
    """Update one agent file with ecosystem sections."""
    content = agent_file.read_text()
    lines = content.split("\n")

    agent_name = agent_file.stem
    agent_title = agent_name.capitalize()
    network = NETWORKS.get(agent_name, "Other agents as relevant")

    # Find Principles section
    principles_idx = next(
        (i for i, line in enumerate(lines) if line.startswith("## Principles")), None
    )
    if principles_idx is None:
        print(f"⚠️  No Principles section in {agent_name}")
        return

    _add_ecosystem_principle(lines, principles_idx, agent_name)
    _replace_memory_section(lines, agent_name, agent_title, network)

    agent_file.write_text("\n".join(lines))


def main():
    """Update all agent files."""
    print("Updating Claude agent definitions for ecosystem collaboration...\n")

    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if agent_file.stem == "bot.example":
            continue
        print(f"Processing {agent_file.name}...")
        update_agent(agent_file)
        print()

    print("✅ All agents updated!")


if __name__ == "__main__":
    main()
