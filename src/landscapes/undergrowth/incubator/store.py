"""Persistence + logging for the incubator.

One SQLite database holds everything worth observing:
  - episodes   one row per agent per daily exploration run
  - steps      every thought, tool call and tool result, in order
  - messages   the shared board agents use to leave notes for each other
  - journal    the one carry-over summary each agent writes at the end of a day
               (this is what "continue where you left off" reads the next day)

Every event is ALSO appended to a per-day JSONL file for easy tailing/analysis.
"""

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from src.landscapes.undergrowth.incubator.config import DB_PATH, LOG_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id      TEXT,
    agent_name    TEXT,
    day           TEXT,
    objective     TEXT,
    started_at    TEXT,
    ended_at      TEXT,
    num_steps     INTEGER,
    num_tool_calls INTEGER,
    summary       TEXT
);
CREATE TABLE IF NOT EXISTS steps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id  INTEGER,
    agent_id    TEXT,
    idx         INTEGER,
    kind        TEXT,           -- thought | tool | summary
    content     TEXT,
    tool_name   TEXT,
    tool_args   TEXT,
    tool_result TEXT,
    ts          TEXT
);
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    from_agent  TEXT,
    from_name   TEXT,
    to_agent    TEXT,           -- an agent id, or "all"
    content     TEXT,
    ts          TEXT,
    read_by     TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS journal (
    agent_id    TEXT,
    day         TEXT,
    summary     TEXT,
    ts          TEXT,
    PRIMARY KEY (agent_id, day)
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Store:
    """Thin, synchronous wrapper over the incubator SQLite db + JSONL log."""

    def __init__(self, db_path: Path = DB_PATH, log_dir: Path = LOG_DIR):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # -- low-level logging --------------------------------------------------
    def _jsonl(self, event: dict) -> None:
        event = {"ts": _now(), **event}
        path = self.log_dir / f"incubator_{date.today().isoformat()}.jsonl"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")

    # -- episodes -----------------------------------------------------------
    def start_episode(self, agent_id, agent_name, objective, day=None) -> int:
        day = day or date.today().isoformat()
        cur = self.conn.execute(
            "INSERT INTO episodes (agent_id, agent_name, day, objective, started_at) "
            "VALUES (?,?,?,?,?)",
            (agent_id, agent_name, day, objective, _now()),
        )
        self.conn.commit()
        ep_id = cur.lastrowid
        self._jsonl(
            {
                "event": "episode_start",
                "episode_id": ep_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "day": day,
                "objective": objective,
            }
        )
        return ep_id

    def end_episode(self, episode_id, num_steps, num_tool_calls, summary) -> None:
        self.conn.execute(
            "UPDATE episodes SET ended_at=?, num_steps=?, num_tool_calls=?, summary=? "
            "WHERE id=?",
            (_now(), num_steps, num_tool_calls, summary, episode_id),
        )
        self.conn.commit()
        self._jsonl(
            {
                "event": "episode_end",
                "episode_id": episode_id,
                "num_steps": num_steps,
                "num_tool_calls": num_tool_calls,
                "summary": summary,
            }
        )

    def log_step(
        self,
        episode_id,
        agent_id,
        idx,
        kind,
        content=None,
        tool_name=None,
        tool_args=None,
        tool_result=None,
    ) -> None:
        self.conn.execute(
            "INSERT INTO steps (episode_id, agent_id, idx, kind, content, "
            "tool_name, tool_args, tool_result, ts) VALUES (?,?,?,?,?,?,?,?,?)",
            (episode_id, agent_id, idx, kind, content, tool_name, tool_args, tool_result, _now()),
        )
        self.conn.commit()
        self._jsonl(
            {
                "event": "step",
                "episode_id": episode_id,
                "agent_id": agent_id,
                "idx": idx,
                "kind": kind,
                "content": content,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "tool_result": (tool_result[:500] if tool_result else None),
            }
        )

    # -- messages (the shared board) ----------------------------------------
    def write_message(self, from_agent, from_name, to_agent, content) -> int:
        cur = self.conn.execute(
            "INSERT INTO messages (from_agent, from_name, to_agent, content, ts) "
            "VALUES (?,?,?,?,?)",
            (from_agent, from_name, to_agent, content, _now()),
        )
        self.conn.commit()
        self._jsonl(
            {
                "event": "message",
                "from_agent": from_agent,
                "from_name": from_name,
                "to_agent": to_agent,
                "content": content,
            }
        )
        return cur.lastrowid

    def read_messages(self, agent_id, mark_read=True, limit=10) -> list[dict]:
        """Messages addressed to this agent (or 'all'), not sent by it, that it
        hasn't already read. Optionally marks them read."""
        rows = self.conn.execute(
            "SELECT * FROM messages "
            "WHERE (to_agent=? OR to_agent='all') AND from_agent!=? "
            "ORDER BY id DESC LIMIT ?",
            (agent_id, agent_id, limit),
        ).fetchall()
        out = []
        for r in rows:
            read_by = set(filter(None, (r["read_by"] or "").split(",")))
            if agent_id in read_by:
                continue
            out.append(dict(r))
            if mark_read:
                read_by.add(agent_id)
                self.conn.execute(
                    "UPDATE messages SET read_by=? WHERE id=?", (",".join(sorted(read_by)), r["id"])
                )
        if mark_read and out:
            self.conn.commit()
        return list(reversed(out))  # oldest first

    def all_messages(self, limit=30) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    # -- journal (daily carry-over memory) ----------------------------------
    def set_journal(self, agent_id, day, summary) -> None:
        self.conn.execute(
            "INSERT INTO journal (agent_id, day, summary, ts) VALUES (?,?,?,?) "
            "ON CONFLICT(agent_id, day) DO UPDATE SET summary=excluded.summary, ts=excluded.ts",
            (agent_id, day, summary, _now()),
        )
        self.conn.commit()

    def last_journal(self, agent_id, before_day=None) -> dict | None:
        """The most recent journal entry (optionally strictly before a day)."""
        if before_day:
            row = self.conn.execute(
                "SELECT * FROM journal WHERE agent_id=? AND day<? ORDER BY day DESC LIMIT 1",
                (agent_id, before_day),
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT * FROM journal WHERE agent_id=? ORDER BY day DESC LIMIT 1",
                (agent_id,),
            ).fetchone()
        return dict(row) if row else None

    def recent_journals(self, agent_id, limit=5) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM journal WHERE agent_id=? ORDER BY day DESC LIMIT ?",
            (agent_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    # -- observation helpers ------------------------------------------------
    def recent_episodes(self, agent_id=None, limit=10) -> list[dict]:
        if agent_id:
            rows = self.conn.execute(
                "SELECT * FROM episodes WHERE agent_id=? ORDER BY id DESC LIMIT ?",
                (agent_id, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM episodes ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def episode_steps(self, episode_id) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM steps WHERE episode_id=? ORDER BY idx", (episode_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
