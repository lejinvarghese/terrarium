"""Build agent prompts with persona, time, and profile facts for scheduled commands."""

import sys
from datetime import datetime
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.engine import memory_store, user_db  # noqa: E402

AGENTS_DIR = Path(__file__).resolve().parents[2] / ".claude" / "agents"


def render_now() -> str:
    """Current date, weekday and time in the host's local timezone."""
    now = datetime.now().astimezone()
    return (
        "## Current date and time\n"
        "\n"
        f"It is **{now:%A, %-d %B %Y, %-I:%M %p}** "
        f"({now.tzname()}, UTC{now:%z}).\n"
        "\n"
        "This is the authoritative local time. Take the date, the day of the week\n"
        "and the clock time from here.\n"
        "\n"
        "`get-current-time` returns a UTC instant and an unreliable `isDST` flag.\n"
        "Use it to convert calendar timestamps, not to tell the time.\n"
    )


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
    click.echo("\n---\n")
    click.echo(render_now())

    if no_profile:
        return

    # Resolve audience: explicit --user flag, or check agent_audiences table
    audience = user
    if not audience:
        audience_id = user_db.get_agent_audience(agent.lower())
        if audience_id:
            audience = audience_id

    try:
        block = memory_store.render_profile(audience)
    except Exception as e:
        # Emit the persona without facts rather than failing the run.
        click.echo(f"\n<!-- profile unavailable: {e} -->", err=True)
        return

    if block:
        click.echo("\n---\n")
        click.echo(block)


if __name__ == "__main__":
    main()
