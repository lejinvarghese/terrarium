#!/usr/bin/env python3
"""Inspect agent memories and session data"""

import sqlite3
from pathlib import Path

import click


def get_db_path():
    """Get path to incubator database."""
    return Path(__file__).parent.parent.parent / "data" / "incubator.db"


@click.group()
def cli():
    """Inspect agent memories and sessions."""
    pass


@cli.command()
@click.option("--agent", "-a", help="Filter by agent ID (e.g., A001)")
@click.option("--limit", "-n", default=10, help="Number of entries to show")
def memories(agent, limit):
    """View agent memories."""
    db_path = get_db_path()

    if not db_path.exists():
        click.secho(f"Database not found: {db_path}", fg="red")
        return

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        query = "SELECT * FROM memories"
        params = []

        if agent:
            query += " WHERE user_id = ?"
            params.append(agent)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            click.secho("No memories found", fg="yellow")
            return

        click.secho(f"\n📝 Found {len(rows)} memories:\n", fg="cyan", bold=True)

        for row in rows:
            click.secho(f"[{row['user_id']}] {row['created_at']}", fg="blue")
            click.secho(f"  {row['memory']}", fg="white")
            click.secho("")


@cli.command()
@click.option("--agent", "-a", help="Filter by agent ID")
@click.option("--limit", "-n", default=5, help="Number of sessions to show")
def sessions(agent, limit):
    """View agent sessions."""
    db_path = get_db_path()

    if not db_path.exists():
        click.secho(f"Database not found: {db_path}", fg="red")
        return

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        query = "SELECT * FROM sessions"
        params = []

        if agent:
            query += " WHERE user_id = ?"
            params.append(agent)

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            click.secho("No sessions found", fg="yellow")
            return

        click.secho(f"\n💬 Found {len(rows)} sessions:\n", fg="cyan", bold=True)

        for row in rows:
            click.secho(f"[{row['id']}] Agent: {row['user_id']}", fg="green")
            click.secho(f"  Created: {row['created_at']}", fg="blue")
            click.secho(f"  Updated: {row['updated_at']}", fg="blue")
            if row.get("summary"):
                click.secho(f"  Summary: {row['summary'][:100]}...", fg="white")
            click.secho("")


@cli.command()
def stats():
    """Show database statistics."""
    db_path = get_db_path()

    if not db_path.exists():
        click.secho(f"Database not found: {db_path}", fg="red")
        return

    with sqlite3.connect(db_path) as conn:
        # Count memories per agent
        cursor = conn.execute(
            """
            SELECT user_id, COUNT(*) as count
            FROM memories
            GROUP BY user_id
            ORDER BY count DESC
        """
        )
        memory_counts = cursor.fetchall()

        # Count sessions per agent
        cursor = conn.execute(
            """
            SELECT user_id, COUNT(*) as count
            FROM sessions
            GROUP BY user_id
            ORDER BY count DESC
        """
        )
        session_counts = cursor.fetchall()

        # Total counts
        total_memories = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        total_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

        click.secho("\n📊 Database Statistics\n", fg="cyan", bold=True)

        click.secho(f"Total Memories: {total_memories}", fg="green")
        click.secho(f"Total Sessions: {total_sessions}", fg="green")

        if memory_counts:
            click.secho("\nMemories by Agent:", fg="yellow")
            for row in memory_counts:
                click.secho(f"  {row[0]}: {row[1]} memories", fg="white")

        if session_counts:
            click.secho("\nSessions by Agent:", fg="yellow")
            for row in session_counts:
                click.secho(f"  {row[0]}: {row[1]} sessions", fg="white")

        click.secho("")


if __name__ == "__main__":
    cli()
