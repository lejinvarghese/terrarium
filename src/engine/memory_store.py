"""Qdrant-backed memory store for Terrarium.

Points carry a `category` in their payload:

    profile   - identity facts. Fetched by exact filter and injected verbatim
                into agent prompts.
    episodic  - activity and conversation history. Fetched by vector similarity.

Text is stored exactly as given; nothing rewrites or summarises it on write.
"""

import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("MEMORY_COLLECTION", "mem0")
EMBED_MODEL = "text-embedding-3-small"
EMBED_DIMS = 1536

USER_ID = os.getenv("TELEGRAM_CHAT_ID")
DANIELLE_USER_ID = os.getenv("DANIELLE_TELEGRAM_CHAT_ID")

PROFILE = "profile"
EPISODIC = "episodic"

# Friendly names accepted anywhere a user_id is expected.
USER_ALIASES = {
    "lejin": USER_ID,
    "me": USER_ID,
    "main": USER_ID,
    "danielle": DANIELLE_USER_ID,
    "dani": DANIELLE_USER_ID,
}


def resolve_user(user_id: str | None) -> str:
    """Map a friendly name or raw chat ID to a chat ID. Defaults to the main user."""
    if not user_id:
        if not USER_ID:
            raise RuntimeError("TELEGRAM_CHAT_ID not set; cannot resolve default user")
        return USER_ID
    resolved = USER_ALIASES.get(str(user_id).strip().lower())
    return resolved or str(user_id)


def embed(text: str) -> list[float]:
    """Embed one string with the same model the collection was built with."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    resp = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"input": text, "model": EMBED_MODEL},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


def _qdrant(method: str, path: str, payload: dict | None = None) -> dict:
    resp = httpx.request(
        method,
        f"{QDRANT_URL}/collections/{COLLECTION}{path}",
        json=payload,
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


def _filter(**terms) -> dict | None:
    """Build a Qdrant `must` filter from non-None keyword terms."""
    must = [{"key": k, "match": {"value": v}} for k, v in terms.items() if v is not None]
    return {"must": must} if must else None


def add_fact(
    data: str,
    user_id: str | None = None,
    agent_id: str = "system",
    category: str = EPISODIC,
) -> dict:
    """Store one memory verbatim.

    Deduplicates on exact content hash. Near-duplicates are stored as distinct
    memories. Returns the new point, or the existing one if the text matches.
    """
    data = data.strip()
    if not data:
        return {"error": "empty memory"}

    target_user = resolve_user(user_id)
    content_hash = hashlib.md5(data.encode()).hexdigest()

    existing = _qdrant(
        "POST",
        "/points/scroll",
        {
            "filter": _filter(user_id=target_user, hash=content_hash),
            "limit": 1,
            "with_payload": True,
        },
    )["result"]["points"]
    if existing:
        return {"status": "duplicate", "id": existing[0]["id"], "data": data}

    point_id = str(uuid.uuid4())
    _qdrant(
        "PUT",
        "/points?wait=true",
        {
            "points": [
                {
                    "id": point_id,
                    "vector": embed(data),
                    "payload": {
                        "user_id": target_user,
                        "agent_id": agent_id or "system",
                        "category": category,
                        "data": data,
                        "hash": content_hash,
                        "created_at": datetime.now().astimezone().isoformat(),
                    },
                }
            ]
        },
    )
    return {"status": "added", "id": point_id, "data": data, "category": category}


def get_profile(user_id: str | None = None) -> list[str]:
    """Return every profile fact for a user, ordered by creation time.

    Exact filter, not a similarity search: the result is always complete.
    """
    target_user = resolve_user(user_id)
    facts, offset = [], None
    while True:
        body = {
            "filter": _filter(user_id=target_user, category=PROFILE),
            "limit": 256,
            "with_payload": True,
            "with_vector": False,
        }
        if offset:
            body["offset"] = offset
        result = _qdrant("POST", "/points/scroll", body)["result"]
        facts.extend(
            (p["payload"].get("created_at") or "", p["payload"]["data"]) for p in result["points"]
        )
        offset = result.get("next_page_offset")
        if not offset:
            break
    return [data for _, data in sorted(facts)]


def get_all(
    user_id: str | None = None,
    agent_id: str | None = None,
    category: str | None = None,
    limit: int = 1000,
) -> list[dict]:
    """List memories by exact filter, newest first."""
    points, offset = [], None
    while len(points) < limit:
        body = {
            "filter": _filter(user_id=resolve_user(user_id), agent_id=agent_id, category=category),
            "limit": min(256, limit - len(points)),
            "with_payload": True,
            "with_vector": False,
        }
        if offset:
            body["offset"] = offset
        result = _qdrant("POST", "/points/scroll", body)["result"]
        points.extend(result["points"])
        offset = result.get("next_page_offset")
        if not offset:
            break
    return sorted(
        (
            {
                "id": p["id"],
                "memory": p["payload"]["data"],
                "agent_id": p["payload"].get("agent_id"),
                "category": p["payload"].get("category"),
                "created_at": p["payload"].get("created_at"),
            }
            for p in points
        ),
        key=lambda m: m["created_at"] or "",
        reverse=True,
    )


def search(
    query: str,
    user_id: str | None = None,
    agent_id: str | None = None,
    category: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Vector search over episodic memory (or any category you name)."""
    result = _qdrant(
        "POST",
        "/points/search",
        {
            "vector": embed(query),
            "filter": _filter(user_id=resolve_user(user_id), agent_id=agent_id, category=category),
            "limit": limit,
            "with_payload": True,
        },
    )["result"]
    return [
        {
            "id": p["id"],
            "memory": p["payload"]["data"],
            "score": p["score"],
            "agent_id": p["payload"].get("agent_id"),
            "category": p["payload"].get("category"),
            "created_at": p["payload"].get("created_at"),
        }
        for p in result
    ]


def render_profile(user_id: str | None = None, heading: str | None = None) -> str:
    """Profile facts as a markdown block, ready to concatenate onto a prompt."""
    facts = get_profile(user_id)
    if not facts:
        return ""
    title = heading or "Known facts about the person you're writing to"
    lines = [
        f"## {title}",
        "",
        "Treat these as ground truth. They override anything you infer, anything you",
        "remember sending before, and any example in this prompt.",
        "",
    ]
    lines += [f"- {f}" for f in facts]
    return "\n".join(lines) + "\n"
