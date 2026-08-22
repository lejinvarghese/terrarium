"""Compose an agent prompt: persona definition + profile facts from Qdrant.

Replaces `cat .claude/agents/<agent>.md` in scheduled commands. The persona file
says how the agent behaves; Qdrant says who it is writing to. Keeping the second
part out of the persona file means there is exactly one place to correct a fact.

    uv run python -m src.engine.build_prompt pepper --user danielle
"""

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.engine import memory_store  # noqa: E402

AGENTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "agents"

# Agents that write to someone other than the main user.
AGENT_AUDIENCE = {"pepper": "danielle"}


@click.command()
@click.argument("agent")
@click.option("--user", default=None, help="Whose profile to inject (name or chat ID).")
@click.option("--no-profile", is_flag=True, help="Persona only, skip profile facts.")
def main(agent, user, no_profile):
    """Print AGENT's persona prompt with their audience's profile facts appended."""
    persona_path = AGENTS_DIR / f"{agent}.md"
    if not persona_path.exists():
        raise click.ClickException(f"No persona file at {persona_path}")

    click.echo(persona_path.read_text().rstrip())

    if no_profile:
        return

    audience = user or AGENT_AUDIENCE.get(agent.lower())
    try:
        block = memory_store.render_profile(audience)
    except Exception as e:
        # A profile we cannot reach is worth shouting about, but it must not stop
        # the agent running - a briefing without facts beats no briefing.
        click.echo(f"\n<!-- profile unavailable: {e} -->", err=True)
        return

    if block:
        click.echo("\n---\n")
        click.echo(block)


if __name__ == "__main__":
    main()
