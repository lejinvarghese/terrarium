"""The five tools an incubator agent has. Stdlib-only, no MCP subprocesses.

  web_search(query)            Tavily if a key is set, else DuckDuckGo (keyless).
  web_fetch(url)               Fetch a page and return cleaned, truncated text.
  read_message()               Read notes peers left for this agent.
  write_message(to, content)   Leave a note for another agent (id, or "all").
  send_telegram_message(text)  Send a message to the user via Telegram (when warranted).

`Toolbox` binds the tools to one agent + the shared Store and exposes:
  .schemas    OpenAI-format tool definitions for the Ollama `tools=` param
  .call(name, args) -> str    dispatch + always return a string result
"""

import html
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

# Load .env for TELEGRAM_TOKEN and other env vars
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # dotenv not available, rely on shell environment

from src.landscapes.undergrowth.incubator.config import (
    TAVILY_KEY_ENV_VARS,
    USE_TAVILY,
    WEB_FETCH_MAX_CHARS,
    WEB_SEARCH_RESULTS,
)

_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"


# Files scanned for the Tavily key when it isn't already in the environment, so
# the scheduler/cron work without an interactive shell. Secrets stay in these
# files — never in the repo.
_ENV_FILES = ("~/.zshrc", "~/.env", "~/dev/.env")


def _extract_env_value(line: str, pattern) -> str | None:
    """Extract and clean environment variable value from a line."""
    match = pattern.match(line)
    if not match:
        return None

    val = match.group(1).strip().strip('"').strip("'")
    return val if val else None


def _read_env_file(path: str) -> list[str]:
    """Read environment file, return empty list on error."""
    from pathlib import Path

    try:
        return Path(path).expanduser().read_text().splitlines()
    except OSError:
        return []


def _key_from_files(var: str) -> str | None:
    import re

    pattern = re.compile(rf"^\s*(?:export\s+)?{re.escape(var)}\s*=\s*(.+?)\s*$")

    for path in _ENV_FILES:
        for line in _read_env_file(path):
            val = _extract_env_value(line, pattern)
            if val:
                return val
    return None


def _tavily_key() -> str | None:
    if not USE_TAVILY:
        return None
    for var in TAVILY_KEY_ENV_VARS:
        key = os.environ.get(var) or _key_from_files(var)
        if key:
            return key
    return None


def _tavily_search(query: str, n: int) -> list[dict]:
    key = _tavily_key()
    if not key:
        return []
    body = {
        "query": query,
        "max_results": min(n, 10),
        "topic": "general",
        "search_depth": "basic",
        "include_raw_content": False,
    }
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read())
    out = []
    for r in data.get("results", []):
        out.append(
            {
                "title": (r.get("title") or "").strip(),
                "url": r.get("url") or "",
                "snippet": " ".join((r.get("content") or "").split())[:280],
            }
        )
    return out


def _ddg_search(query: str, n: int) -> list[dict]:
    data = urllib.parse.urlencode({"q": query}).encode()
    req = urllib.request.Request(
        "https://html.duckduckgo.com/html/",
        data=data,
        headers={"User-Agent": _UA},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read().decode("utf-8", "ignore")
    results, seen = [], set()
    # each result: an anchor with class result__a (title+href) then a snippet anchor
    pattern = re.compile(
        r'result__a"[^>]*href="([^"]+)".*?>(.*?)</a>.*?' r'(?:result__snippet"[^>]*>(.*?)</a>)?',
        re.DOTALL,
    )
    for m in pattern.finditer(raw):
        url, title, snippet = m.group(1), m.group(2), m.group(3) or ""
        # DDG wraps external links in a redirect; unwrap uddg=
        if "uddg=" in url:
            url = urllib.parse.unquote(url.split("uddg=", 1)[1].split("&", 1)[0])
        title = html.unescape(re.sub("<[^>]+>", "", title)).strip()
        snippet = html.unescape(re.sub("<[^>]+>", "", snippet)).strip()
        if not title or url in seen:
            continue
        seen.add(url)
        results.append({"title": title, "url": url, "snippet": snippet[:280]})
        if len(results) >= n:
            break
    return results


def web_search(query: str, max_results: int = WEB_SEARCH_RESULTS) -> str:
    """Search the web; Tavily first, DuckDuckGo fallback. Returns a compact block."""
    query = (query or "").strip()
    if not query:
        return "web_search error: empty query."
    results, backend = [], "tavily"
    try:
        results = _tavily_search(query, max_results)
    except Exception:
        results = []
    if not results:
        backend = "duckduckgo"
        try:
            results = _ddg_search(query, max_results)
        except Exception as e:
            return f"web_search failed for {query!r}: {e}"
    if not results:
        return f"web_search: no results for {query!r}."
    lines = [f"Search results for {query!r} (via {backend}):"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}\n   {r['url']}")
        if r["snippet"]:
            lines.append(f"   {r['snippet']}")
    return "\n".join(lines)


def web_fetch(url: str, max_chars: int = WEB_FETCH_MAX_CHARS) -> str:
    """Fetch a URL and return cleaned, truncated page text."""
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        return f"web_fetch error: {url!r} is not a valid http(s) URL."
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=25) as resp:
            ctype = resp.headers.get("Content-Type", "")
            raw = resp.read(2_000_000)
    except Exception as e:
        return f"web_fetch failed for {url}: {e}"
    if "html" not in ctype and "text" not in ctype and not url.endswith((".html", "/")):
        return f"web_fetch: {url} is not text ({ctype})."
    text = raw.decode("utf-8", "ignore")
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + " …[truncated]"
    return f"Fetched {url}:\n{text}"


def _send_telegram_via_api(chat_id: int, text: str, agent_name: str) -> bool:
    """Send a message via Telegram Bot API (synchronous, no bot instance needed)."""
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        return False
    # Prefix message with agent name so user knows who's talking
    formatted_text = f"🌱 *{agent_name}*\n\n{text}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = {
        "chat_id": chat_id,
        "text": formatted_text,
        "parse_mode": "Markdown",
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# Tool schemas (OpenAI function-calling format, what Ollama expects)
# --------------------------------------------------------------------------- #
def _recipients() -> list[str]:
    """Who can be messaged, from the user database. Never hardcode people here."""
    try:
        from src.engine import user_db

        return [u["username"] for u in user_db.get_db().list_users()]
    except Exception:
        return []


def _telegram_schema() -> dict:
    """The Telegram tool, with its recipients resolved at load time."""
    to_user = {
        "type": "string",
        "description": "who to send it to - omit to reach the primary user",
    }
    known = _recipients()
    if known:
        to_user["enum"] = known

    return {
        "type": "function",
        "function": {
            "name": "send_telegram_message",
            "description": (
                "Send a discovery to someone via Telegram. Use it when you find "
                "something interesting, and pick whoever is most likely to care. "
                "Be enthusiastic and brief!"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "your discovery message - exciting and brief",
                    },
                    "to_user": to_user,
                },
                "required": ["text"],
            },
        },
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information on any topic. Returns titles, URLs and snippets.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "what to search for"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch and read the full text of a web page by its URL.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "the http(s) URL to read"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_message",
            "description": "Read notes that other agents have left for you.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_message",
            "description": "Share a discovery with another agent. Use when you find something they'd find interesting - call this right after web_fetch when the content is relevant to a peer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "recipient: A001 (tech/research), A002 (music/art), A003 (philosophy), or 'all'",
                    },
                    "content": {
                        "type": "string",
                        "description": "what you found that they'd care about",
                    },
                },
                "required": ["to", "content"],
            },
        },
    },
    _telegram_schema(),
]


class Toolbox:
    """Binds the tools to one agent and the shared Store.

    `allow` narrows the toolset for contexts that need only some of it - a
    conversation, for instance, wants research but no way to answer somewhere
    other than where it was asked.
    """

    schemas = TOOL_SCHEMAS

    def __init__(self, store, agent_id: str, agent_name: str, allow: tuple[str, ...] | None = None):
        self.store = store
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.allow = set(allow) if allow else None
        self.schemas = (
            TOOL_SCHEMAS
            if self.allow is None
            else [s for s in TOOL_SCHEMAS if s["function"]["name"] in self.allow]
        )

    def call(self, name: str, args: dict) -> str:
        args = args or {}
        if self.allow is not None and name not in self.allow:
            return f"{name} is not available here."
        try:
            if name == "web_search":
                return web_search(args.get("query", ""))
            if name == "web_fetch":
                return web_fetch(args.get("url", ""))
            if name == "read_message":
                return self._read_message()
            if name == "write_message":
                return self._write_message(args.get("to", ""), args.get("content", ""))
            if name == "send_telegram_message":
                return self._send_telegram_message(args.get("text", ""), args.get("to_user"))
            return f"Unknown tool: {name}"
        except Exception as e:
            return f"Tool {name} error: {e}"

    def _read_message(self) -> str:
        msgs = self.store.read_messages(self.agent_id, mark_read=True)
        if not msgs:
            return "No new messages."
        return "\n".join(f"From {m['from_name']} ({m['from_agent']}): {m['content']}" for m in msgs)

    def _write_message(self, to: str, content: str) -> str:
        to = (to or "all").strip()
        content = (content or "").strip()
        if not content:
            return "write_message error: empty content."
        self.store.write_message(self.agent_id, self.agent_name, to, content)
        return f"Message left for {to}."

    def _send_telegram_message(self, text: str, to_user: str | None = None) -> str:
        """Send a Telegram message. The recipient is resolved from the user database."""
        text = (text or "").strip()
        if not text:
            return "send_telegram_message error: empty text."

        from src.engine import user_db

        recipient = (to_user or "").strip().lower() or None
        try:
            chat_id = int(user_db.resolve_user_id(recipient))
        except (ValueError, TypeError):
            return f"send_telegram_message error: no known recipient '{to_user}'."

        if _send_telegram_via_api(chat_id, text, self.agent_name):
            return f"Message sent to {recipient or 'the primary user'} via Telegram."
        else:
            return (
                "send_telegram_message failed: could not reach Telegram API. "
                "Message saved in your journal instead."
            )
