#!/usr/bin/env python3
"""Observe what the incubator agents have been doing.

  python -m src.landscapes.undergrowth.incubator.observe episodes [-a A001]
  python -m src.landscapes.undergrowth.incubator.observe journal  [-a A001]
  python -m src.landscapes.undergrowth.incubator.observe messages
  python -m src.landscapes.undergrowth.incubator.observe steps -e <episode_id>
"""

import click

from src.landscapes.undergrowth.incubator.store import Store

_KIND_ICON = {"thought": "💭", "tool": "🔧", "summary": "📔"}


@click.group()
def cli():
    """Inspect the incubator's SQLite logs."""


@cli.command()
@click.option("--agent", "-a", default=None, help="Filter by agent id")
@click.option("--limit", "-n", default=10)
def episodes(agent, limit):
    """List recent episodes."""
    store = Store()
    for ep in store.recent_episodes(agent, limit):
        click.secho(f"#{ep['id']}  {ep['agent_name']} ({ep['agent_id']})  {ep['day']}",
                    fg="green", bold=True)
        click.echo(f"    goal: {ep['objective']}")
        click.echo(f"    {ep['num_steps']} steps · {ep['num_tool_calls']} tool calls")
        if ep["summary"]:
            click.secho(f"    📔 {ep['summary']}", fg="yellow")
        click.echo()
    store.close()


@cli.command()
@click.option("--agent", "-a", default=None, help="Filter by agent id")
@click.option("--limit", "-n", default=5)
def journal(agent, limit):
    """Show agents' carry-over journal entries."""
    store = Store()
    agents = [agent] if agent else [e["agent_id"] for e in store.recent_episodes(limit=50)]
    seen = set()
    for aid in agents:
        if aid in seen:
            continue
        seen.add(aid)
        entries = store.recent_journals(aid, limit)
        if not entries:
            continue
        click.secho(f"=== {aid} ===", fg="cyan", bold=True)
        for j in entries:
            click.secho(f"  {j['day']}", fg="green")
            click.echo(f"    {j['summary']}")
        click.echo()
    store.close()


@cli.command()
@click.option("--limit", "-n", default=30)
def messages(limit):
    """Show the shared message board."""
    store = Store()
    msgs = store.all_messages(limit)
    if not msgs:
        click.echo("(no messages yet)")
    for m in msgs:
        read = f" · read by {m['read_by']}" if m["read_by"] else " · unread"
        click.secho(f"{m['from_name']} ({m['from_agent']}) → {m['to_agent']}{read}",
                    fg="magenta")
        click.echo(f"    {m['content']}")
    store.close()


@cli.command()
@click.option("--episode", "-e", required=True, type=int, help="Episode id")
def steps(episode):
    """Show every step of one episode, in order."""
    store = Store()
    rows = store.episode_steps(episode)
    if not rows:
        click.echo(f"(no steps for episode {episode})")
    for s in rows:
        icon = _KIND_ICON.get(s["kind"], "·")
        if s["kind"] == "tool":
            click.secho(f"  {icon} {s['tool_name']}({s['tool_args']})", fg="blue")
            click.echo(f"       → {(s['tool_result'] or '')[:200].strip()}")
        else:
            click.secho(f"  {icon} {(s['content'] or '').strip()[:300]}", fg="white")
    store.close()


if __name__ == "__main__":
    cli()
