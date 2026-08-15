"""Logging system for capturing teacher episodes for student model distillation"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


class DistillationLogger:
    """Logger for capturing agent episodes in training-ready format.

    Saves episodes in ChatML format suitable for fine-tuning student models
    via QLoRA or similar techniques.
    """

    def __init__(self, db_path: str | Path):
        """Initialize distillation logger.

        Args:
            db_path: Path to SQLite database for storing episodes
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS distillation_episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id TEXT UNIQUE NOT NULL,
                    agent_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    messages_json TEXT NOT NULL,
                    tools_used TEXT,
                    quality TEXT DEFAULT 'medium',
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()

    def log_episode(
        self,
        episode_id: str,
        agent_config: dict,
        messages: list[dict],
        tools_used: list[str] = None,
        quality: str = "medium",
        tags: list[str] = None,
        **metadata,
    ):
        """Log an episode in distillation-ready format.

        Args:
            episode_id: Unique episode identifier
            agent_config: Agent configuration dict
            messages: List of message dicts in ChatML format
            tools_used: List of tool names called during episode
            quality: Episode quality rating (high/medium/low)
            tags: Additional tags for filtering
            **metadata: Additional metadata (model_type, model_name, etc.)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO distillation_episodes
                (episode_id, agent_id, agent_name, timestamp, model_type, model_name,
                 objective, messages_json, tools_used, quality, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    episode_id,
                    agent_config["id"],
                    agent_config["name"],
                    datetime.now().isoformat(),
                    metadata.get("model_type", "unknown"),
                    metadata.get("model_name", "unknown"),
                    metadata.get("objective", ""),
                    json.dumps(messages),
                    json.dumps(tools_used or []),
                    quality,
                    json.dumps(tags or []),
                ),
            )
            conn.commit()

    def get_episodes(
        self, agent_id: str = None, quality: str = None, limit: int = 100
    ) -> list[dict]:
        """Retrieve episodes for export.

        Args:
            agent_id: Filter by agent ID
            quality: Filter by quality (high/medium/low)
            limit: Maximum number of episodes to retrieve

        Returns:
            List of episode dicts
        """
        query = "SELECT * FROM distillation_episodes WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if quality:
            query += " AND quality = ?"
            params.append(quality)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def export_jsonl(
        self,
        output_path: str | Path,
        agent_id: str = None,
        quality: str = "high",
        limit: int = 1000,
    ):
        """Export episodes to JSONL format for training.

        Args:
            output_path: Path to output JSONL file
            agent_id: Filter by agent ID
            quality: Filter by quality
            limit: Maximum episodes to export
        """
        episodes = self.get_episodes(agent_id, quality, limit)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            for episode in episodes:
                messages = json.loads(episode["messages_json"])
                training_example = {
                    "messages": messages,
                    "metadata": {
                        "episode_id": episode["episode_id"],
                        "agent_id": episode["agent_id"],
                        "agent_name": episode["agent_name"],
                        "quality": episode["quality"],
                        "tools_used": json.loads(episode["tools_used"]),
                    },
                }
                f.write(json.dumps(training_example) + "\n")

        return len(episodes)

    def assess_quality(self, episode_data: dict) -> str:
        """Assess episode quality for training.

        Args:
            episode_data: Episode data dict

        Returns:
            Quality rating: "high", "medium", or "low"
        """
        tools_used = episode_data.get("tools_used", [])
        steps = episode_data.get("steps", 0)

        # High quality: multiple tool calls, good length
        if len(tools_used) >= 2 and steps >= 3:
            return "high"

        # Medium quality: some tool calls or decent length
        elif len(tools_used) >= 1 or steps >= 2:
            return "medium"

        # Low quality: minimal interaction
        else:
            return "low"
