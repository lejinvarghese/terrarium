#!/usr/bin/env python
"""Session Manager - SQLite-based persistence for Claude sessions."""

import sqlite3
import click
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager


class SessionManager:
    """
    Manages user sessions with Claude, tracking session IDs per user and persona.
    """

    def __init__(self, db_path: str = "data/sessions.db"):
        """
        Initialize Session Manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        click.secho(f"💾 SessionManager initialized: {self.db_path}", fg="blue")

    def _init_db(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    persona TEXT,
                    session_id TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, persona)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    message_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            click.secho("📊 Database tables initialized", fg="green")

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_session(self, user_id: int, persona: Optional[str] = None, max_age_hours: int = 24) -> Optional[str]:
        """
        Get active session ID for user and persona, with automatic expiry.

        Args:
            user_id: Telegram user ID
            persona: Persona name (optional, defaults to None for general chat)
            max_age_hours: Maximum hours since last message before expiry (default: 24)

        Returns:
            Claude session ID, or None if no active session or session expired
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT session_id,
                       ROUND((JULIANDAY('now') - JULIANDAY(updated_at)) * 24, 1) as hours_since_last_message
                FROM sessions
                WHERE user_id = ? AND persona IS ?
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (user_id, persona),
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Check if session expired
            hours_old = row["hours_since_last_message"]
            if hours_old > max_age_hours:
                click.secho(
                    f"⏰ Session expired ({hours_old:.1f}h since last message) - user={user_id}, bot={persona or 'casper'}",
                    fg="yellow"
                )
                self.clear_session(user_id, persona)
                return None

            return row["session_id"]

    def create_session(
        self,
        user_id: int,
        session_id: str,
        persona: Optional[str] = None,
    ) -> int:
        """
        Create or update a session.

        Args:
            user_id: Telegram user ID
            session_id: Claude session ID
            persona: Persona name

        Returns:
            Database row ID
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO sessions (user_id, persona, session_id, message_count, updated_at)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, persona) DO UPDATE SET
                    session_id = excluded.session_id,
                    message_count = message_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, persona, session_id),
            )
            conn.commit()
            click.secho(
                f"💬 Session saved: user={user_id}, bot={persona or 'casper'}",
                fg="cyan",
            )
            return cursor.lastrowid

    def update_session_metadata(
        self,
        user_id: int,
        persona: Optional[str],
        cost: Optional[float] = None,
    ):
        """
        Update session metadata after a message.

        Args:
            user_id: Telegram user ID
            persona: Persona name
            cost: Message cost to add
        """
        with self._get_connection() as conn:
            if cost:
                conn.execute(
                    """
                    UPDATE sessions
                    SET total_cost = total_cost + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND persona IS ?
                    """,
                    (cost, user_id, persona),
                )
            else:
                conn.execute(
                    """
                    UPDATE sessions
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND persona IS ?
                    """,
                    (user_id, persona),
                )
            conn.commit()

    def clear_session(self, user_id: int, persona: Optional[str] = None):
        """
        Clear session for user and persona.

        Args:
            user_id: Telegram user ID
            persona: Persona name (None = clear current persona)
        """
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM sessions WHERE user_id = ? AND persona IS ?",
                (user_id, persona),
            )
            conn.commit()
            click.secho(
                f"🗑️  Session cleared: user={user_id}, bot={persona or 'casper'}",
                fg="yellow",
            )

    def clear_all_sessions(self, user_id: int):
        """
        Clear all sessions for a user.

        Args:
            user_id: Telegram user ID
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()
            click.secho(f"🗑️  All sessions cleared for user={user_id}", fg="red")

    def get_session_info(
        self, user_id: int, persona: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get session information.

        Args:
            user_id: Telegram user ID
            persona: Persona name

        Returns:
            Session info dict, or None if no session
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT session_id, message_count, total_cost, created_at, updated_at
                FROM sessions
                WHERE user_id = ? AND persona IS ?
                """,
                (user_id, persona),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def list_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        List all active sessions for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            List of session info dicts
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT persona, session_id, message_count, total_cost, updated_at
                FROM sessions
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def register_user(self, user_id: int, username: str = None, first_name: str = None):
        """
        Register or update user information.

        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, username, first_name, message_count, last_active)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    message_count = message_count + 1,
                    last_active = CURRENT_TIMESTAMP
                """,
                (user_id, username, first_name),
            )
            conn.commit()

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user statistics.

        Args:
            user_id: Telegram user ID

        Returns:
            User stats dict, or None if user not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT u.username, u.first_name, u.message_count, u.created_at, u.last_active,
                       COUNT(s.id) as active_sessions,
                       COALESCE(SUM(s.total_cost), 0) as total_cost
                FROM users u
                LEFT JOIN sessions s ON u.user_id = s.user_id
                WHERE u.user_id = ?
                GROUP BY u.user_id
                """,
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
