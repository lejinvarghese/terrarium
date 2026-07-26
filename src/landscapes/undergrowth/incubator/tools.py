"""The four tools an incubator agent has. Stdlib-only, no MCP subprocesses.

  web_search(query)            Tavily if a key is set, else DuckDuckGo (keyless).
  web_fetch(url)               Fetch a page and return cleaned, truncated text.
  read_message()               Read notes peers left for this agent.
  write_message(to, content)   Leave a note for another agent (id, or "all").

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


def _key_from_files(var: str) -> str | None:
    import re
    from pathlib import Path
    pat = re.compile(rf"^\s*(?:export\s+)?{re.escape(var)}\s*=\s*(.+?)\s*$")
    for path in _ENV_FILES:
        try:
            for line in Path(path).expanduser().read_text().splitlines():
                m = pat.match(line)
                if m:
                    val = m.group(1).strip().strip('"').strip("'")
                    if val:
                        return val
        except OSError:
            continue
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
        out.append({
            "title": (r.get("title") or "").strip(),
            "url": r.get("url") or "",
            "snippet": " ".join((r.get("content") or "").split())[:280],
        })
    return out


def _ddg_search(query: str, n: int) -> list[dict]:
    data = urllib.parse.urlencode({"q": query}).encode()
    req = urllib.request.Request(
        "https://html.duckduckgo.com/html/", data=data,
        headers={"User-Agent": _UA},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read().decode("utf-8", "ignore")
    results, seen = [], set()
    # each result: an anchor with class result__a (title+href) then a snippet anchor
    pattern = re.compile(
        r'result__a"[^>]*href="([^"]+)".*?>(.*?)</a>.*?'
        r'(?:result__snippet"[^>]*>(.*?)</a>)?',
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


# --------------------------------------------------------------------------- #
# Tool schemas (OpenAI function-calling format, what Ollama expects)
# --------------------------------------------------------------------------- #
TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the web for current information on any topic. Returns titles, URLs and snippets.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "what to search for"}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "web_fetch",
        "description": "Fetch and read the full text of a web page by its URL.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string", "description": "the http(s) URL to read"}},
            "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "read_message",
        "description": "Read notes that other agents have left for you.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "write_message",
        "description": "Leave a note for another agent so they see it next time they explore.",
        "parameters": {"type": "object", "properties": {
            "to": {"type": "string", "description": "recipient agent id (e.g. 'A002') or 'all'"},
            "content": {"type": "string", "description": "the message"}},
            "required": ["to", "content"]}}},
]


class Toolbox:
    """Binds the four tools to one agent and the shared Store."""

    schemas = TOOL_SCHEMAS

    def __init__(self, store, agent_id: str, agent_name: str):
        self.store = store
        self.agent_id = agent_id
        self.agent_name = agent_name

    def call(self, name: str, args: dict) -> str:
        args = args or {}
        try:
            if name == "web_search":
                return web_search(args.get("query", ""))
            if name == "web_fetch":
                return web_fetch(args.get("url", ""))
            if name == "read_message":
                return self._read_message()
            if name == "write_message":
                return self._write_message(args.get("to", ""), args.get("content", ""))
            return f"Unknown tool: {name}"
        except Exception as e:
            return f"Tool {name} error: {e}"

    def _read_message(self) -> str:
        msgs = self.store.read_messages(self.agent_id, mark_read=True)
        if not msgs:
            return "No new messages."
        return "\n".join(
            f"From {m['from_name']} ({m['from_agent']}): {m['content']}" for m in msgs
        )

    def _write_message(self, to: str, content: str) -> str:
        to = (to or "all").strip()
        content = (content or "").strip()
        if not content:
            return "write_message error: empty content."
        self.store.write_message(self.agent_id, self.agent_name, to, content)
        return f"Message left for {to}."
