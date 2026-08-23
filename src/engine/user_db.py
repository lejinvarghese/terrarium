"""SQLite user database - stores identities, aliases, and agent audiences."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"


class UserDB:
    """Lightweight SQLite user database."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Create tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    is_primary BOOLEAN NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_aliases (
                    alias TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_audiences (
                    agent_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """
            )

    def add_user(
        self,
        user_id: str,
        username: str,
        full_name: str | None = None,
        is_primary: bool = False,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        """Add user with optional aliases. Returns user record."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO users (user_id, username, full_name, is_primary, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, username, full_name, is_primary, datetime.now().isoformat()),
            )

            # Add aliases
            if aliases:
                for alias in aliases:
                    conn.execute(
                        "INSERT OR REPLACE INTO user_aliases (alias, user_id) VALUES (?, ?)",
                        (alias, user_id),
                    )

        user = self.get_user(user_id)
        if not user:
            raise RuntimeError(f"Failed to create user {user_id}")
        return user

    def get_user(self, identifier: str | None = None) -> dict[str, Any] | None:
        """Get user by ID, username, or alias. None returns primary user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if identifier is None:
                # Get primary user
                row = conn.execute("SELECT * FROM users WHERE is_primary = 1 LIMIT 1").fetchone()
            else:
                # Try direct user_id lookup
                row = conn.execute(
                    "SELECT * FROM users WHERE user_id = ? OR username = ?",
                    (identifier, identifier),
                ).fetchone()

                # Try alias lookup
                if not row:
                    alias_row = conn.execute(
                        "SELECT user_id FROM user_aliases WHERE alias = ?", (identifier,)
                    ).fetchone()
                    if alias_row:
                        row = conn.execute(
                            "SELECT * FROM users WHERE user_id = ?", (alias_row["user_id"],)
                        ).fetchone()

            if row:
                return dict(row)
            return None

    def resolve_user_id(self, identifier: str | None = None) -> str:
        """Resolve username/alias/ID to user_id. None returns primary user."""
        user = self.get_user(identifier)
        if not user:
            if identifier is None:
                raise ValueError("No primary user configured")
            raise ValueError(f"User not found: {identifier}")
        return user["user_id"]

    def get_primary_user(self) -> dict[str, Any] | None:
        """Get the primary user."""
        return self.get_user(None)

    def list_users(self) -> list[dict[str, Any]]:
        """List all users."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM users ORDER BY is_primary DESC, username").fetchall()
            return [dict(row) for row in rows]

    def set_agent_audience(self, agent_id: str, user_id: str):
        """Set default user an agent writes to."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO agent_audiences (agent_id, user_id) VALUES (?, ?)",
                (agent_id, user_id),
            )

    def get_agent_audience(self, agent_id: str) -> str | None:
        """Get agent's default user_id audience."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT user_id FROM agent_audiences WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            return row[0] if row else None


# Global instance
_db = None


def get_db() -> UserDB:
    """Get the global UserDB instance."""
    global _db
    if _db is None:
        _db = UserDB()
    return _db


def resolve_user_id(identifier: str | None = None) -> str:
    """Convenience function to resolve user identifier to user_id."""
    return get_db().resolve_user_id(identifier)


def get_user(identifier: str | None = None) -> dict[str, Any] | None:
    """Convenience function to get user record."""
    return get_db().get_user(identifier)


def get_agent_audience(agent_id: str) -> str | None:
    """Convenience function to get agent's default audience."""
    return get_db().get_agent_audience(agent_id)


if __name__ == "__main__":
    """CLI for user management."""
    import click

    @click.group()
    def cli():
        """Terrarium user database management."""
        pass

    @cli.command()
    def list():
        """List all users."""
        db = get_db()
        users = db.list_users()
        if not users:
            click.echo("No users found. Run scripts/init_users.py for initial setup.")
            return

        for user in users:
            primary = " [PRIMARY]" if user["is_primary"] else ""
            click.echo(f"\n{user['username']}{primary}")
            click.echo(f"  ID: {user['user_id']}")
            click.echo(f"  Full Name: {user['full_name'] or 'N/A'}")

    @cli.command()
    @click.argument("user_id")
    @click.argument("username")
    @click.option("--full-name", default=None, help="Full name")
    @click.option("--primary", is_flag=True, help="Make this the primary user")
    @click.option("--alias", multiple=True, help="Add alias (can be used multiple times)")
    def add(user_id, username, full_name, primary, alias):
        """Add a new user to the database."""
        db = get_db()
        result = db.add_user(
            user_id=user_id,
            username=username,
            full_name=full_name,
            is_primary=primary,
            aliases=list(alias) if alias else None,
        )
        click.echo(f"✓ Added user: {result['username']} ({result['user_id']})")

    @cli.command()
    @click.argument("agent_id")
    @click.argument("user_identifier")
    def set_audience(agent_id, user_identifier):
        """Set which user an agent writes to by default."""
        db = get_db()
        user_id = db.resolve_user_id(user_identifier)
        user = db.get_user(user_id)
        db.set_agent_audience(agent_id, user_id)
        click.echo(f"✓ Agent '{agent_id}' now writes to {user['username']} ({user_id})")

    @cli.command()
    @click.argument("identifier")
    def show(identifier):
        """Show details for a user (by ID, username, or alias)."""
        db = get_db()
        user = db.get_user(identifier)
        if not user:
            click.echo(f"User not found: {identifier}", err=True)
            return

        primary = " [PRIMARY]" if user.get("is_primary") else ""
        click.echo(f"\n{user.get('username')}{primary}")
        click.echo(f"  ID: {user.get('user_id')}")
        click.echo(f"  Full Name: {user.get('full_name') or 'N/A'}")

    cli()
