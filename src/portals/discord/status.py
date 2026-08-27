"""What the terrarium has been doing.

Three sources, one digest: sessions in the current channel (SQLite), what the
scheduler is set to run (configs/schedule.json plus whether the engine process
is alive), and what each agent last actually did - Claude agents from their
episodic memories in Qdrant, incubator agents from their episode log.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

from src.engine import memory_store
from src.landscapes.undergrowth.incubator.store import Store
from src.portals.core.personas import display_name

SCHEDULE_PATH = Path(__file__).parent.parent.parent.parent / "configs" / "schedule.json"
SCHEDULER_PROCESS = "engine.scheduler|engine/scheduler"


def ago(timestamp: str | None) -> str:
    """Render an ISO timestamp as a rough age."""
    if not timestamp:
        return "unknown"
    try:
        then = datetime.fromisoformat(timestamp)
    except ValueError:
        return "unknown"

    minutes = int((datetime.now(then.tzinfo) - then).total_seconds() // 60)
    if minutes < 60:
        return f"{max(minutes, 0)}m ago"
    if minutes < 1440:
        return f"{minutes // 60}h ago"
    return f"{minutes // 1440}d ago"


def _trim(text: str, width: int = 90) -> str:
    """One-line preview of a memory or summary."""
    flat = " ".join((text or "").split())
    return flat[: width - 1] + "…" if len(flat) > width else flat


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def channel_sessions(sessions, channel_id: int) -> str:
    """Which agents are mid-conversation in this channel."""
    rows = sessions.list_user_sessions(channel_id)
    if not rows:
        return "Nobody has spoken here yet."
    return "\n".join(
        f"{display_name(r['persona'])} · {r['message_count']} "
        f"message{'' if r['message_count'] == 1 else 's'} · {ago(r['updated_at'])}"
        for r in rows
    )


def scheduler_status() -> str:
    """Whether the engine is alive, and what it runs today."""
    alive = subprocess.run(
        ["pgrep", "-f", SCHEDULER_PROCESS], capture_output=True, text=True
    ).returncode
    header = "🟢 engine running" if alive == 0 else "🔴 engine stopped"

    try:
        tasks = json.loads(SCHEDULE_PATH.read_text())["tasks"]
    except (OSError, ValueError, KeyError):
        return f"{header}\nNo schedule config found."

    today = datetime.now().strftime("%A").lower()
    due = [t for t in tasks if "day" in t["schedule"] or today in t["schedule"]]
    lines = [f"• {t['name']} — {t['schedule'].removeprefix('every ')}" for t in due[:8]]
    return f"{header} · {len(tasks)} tasks registered\n**Today:**\n" + (
        "\n".join(lines) or "Nothing scheduled today."
    )


def agent_activity(limit: int = 8) -> str:
    """The last thing each Claude agent recorded doing."""
    memories = memory_store.get_all(category="episodic", limit=5000)

    latest: dict[str, dict] = {}
    for memory in memories:  # already newest first
        latest.setdefault(memory.get("agent_id") or "system", memory)

    ranked = sorted(latest.values(), key=lambda m: m["created_at"] or "", reverse=True)
    return "\n".join(
        f"{display_name(m['agent_id'])} · {ago(m['created_at'])}\n-# {_trim(m['memory'])}"
        for m in ranked[:limit]
    )


def incubator_activity(limit: int = 4) -> str:
    """Each local agent's most recent completed exploration."""
    store = Store()
    try:
        episodes = store.recent_episodes(limit=40)
    finally:
        store.close()

    latest: dict[str, dict] = {}
    for episode in episodes:  # already newest first
        if episode["summary"]:
            latest.setdefault(episode["agent_id"], episode)

    if not latest:
        return "No explorations yet."
    return "\n".join(
        f"{display_name(e['agent_name'])} · {ago(e['ended_at'] or e['started_at'])} · "
        f"{e['num_tool_calls'] or 0} tool calls\n-# {_trim(e['summary'])}"
        for e in list(latest.values())[:limit]
    )
