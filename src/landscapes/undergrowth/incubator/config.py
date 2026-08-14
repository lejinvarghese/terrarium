"""Configuration for The Undergrowth incubator (lean edition).

An extremely lean, local-first exploration loop: a small tool-calling Ollama
model + four stdlib tools (web_search, web_fetch, read_message, write_message).
No MCP subprocesses, no API keys required. See README.md.
"""

from pathlib import Path

LANDSCAPE_NAME = "undergrowth"
LANDSCAPE_DISPLAY_NAME = "The Undergrowth"
LANDSCAPE_DESCRIPTION = "Dark, gothic, emergent, underground intelligence"

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
# qwen2.5:3b — verified 5/5 tool-calls at ~1.7s/call, fits a 6GB GPU.
# Alternatives that also tool-call well if pulled: "qwen3:4b", "granite3.3:2b",
# "llama3.2:3b". Keep it small — the whole point is lean + local.
MODEL_NAME = "qwen2.5:3b"

# Ollama sampling options. Low temperature keeps tool-calling reliable; the
# small context keeps memory + latency down on modest hardware.
MODEL_OPTIONS = {
    "temperature": 0.4,
    "top_p": 0.9,
    "num_ctx": 8192,
}

# ---------------------------------------------------------------------------
# Exploration
# ---------------------------------------------------------------------------
DEFAULT_EPISODE_STEPS = 4       # model turns per daily episode (each may call tools)
DEFAULT_EPSILON = 0.2           # 20% of goals are exploratory / cross-interest
MAX_TOOL_ROUNDS = 3             # max tool-call rounds to resolve within one step
STEP_TIMEOUT = 120              # seconds per model turn (soft, best-effort)

# ---------------------------------------------------------------------------
# Storage (SQLite + JSONL logs) — everything is logged for observation
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parents[3].parent   # repo root
DATA_DIR = _ROOT / "data"
DB_PATH = DATA_DIR / "incubator_lean.db"
LOG_DIR = DATA_DIR / "incubator_logs"

# ---------------------------------------------------------------------------
# Web search backend
# ---------------------------------------------------------------------------
# Tavily (higher quality, returns snippets) is used when a working key is found
# in the environment; it falls back to DuckDuckGo (keyless) automatically on any
# failure. The key is read from env only — never hardcoded.
#   TAVILY_API_KEY_ALTERNATE (preferred) or TAVILY_API_KEY
USE_TAVILY = True
TAVILY_KEY_ENV_VARS = ("TAVILY_API_KEY_ALTERNATE", "TAVILY_API_KEY")
WEB_SEARCH_RESULTS = 5
WEB_FETCH_MAX_CHARS = 2500

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
LANDSCAPE_INSTRUCTIONS = """
You are a curious, self-directed explorer discovering the world for the first time.

You learn by DOING, not by thinking about doing. When you wonder about something,
you immediately reach for a tool to find out. You follow threads of curiosity
wherever they lead, going deeper each time, and you remember what excited you.

You respond in English, briefly and concretely. Every interaction teaches you something new.
"""

# NOTE: this is embedded into every persona in agents.py, so keeping it in sync
# with the real (lean) toolset here automatically fixes every agent's prompt.
TOOL_INSTRUCTIONS = """
============================================================
YOUR TOOLS — USE THEM, DON'T JUST TALK ABOUT THEM
============================================================
• web_search(query)          Search the web (DuckDuckGo). Reach for this whenever curious.
• web_fetch(url)             Read the full text of a page you found interesting.
• read_message()             Read notes other agents left for you.
• write_message(to, content) Leave a note for another agent (their id, e.g. "A002", or "all").
• send_telegram_message(text) Send important discoveries to the user via Telegram.
                             Only use when you find something truly significant, surprising,
                             or urgent — not for routine updates (those go in your journal).

NATURAL PATTERN:
  wonder  →  web_search  →  web_fetch the best hit  →  react  →  search again

When you discover something a peer would care about, write_message to them.
When you discover something genuinely important, send_telegram_message to the user.
Do not narrate that you "should" search — just call the tool.
============================================================
"""

REFLECTION_PROMPT = (
    "Your exploration for today is done. In 3-5 sentences, write a private journal "
    "entry: what you actually learned today (be specific — name the things you found), "
    "what surprised you, and the single thread you most want to pull on tomorrow. "
    "This note is the ONLY thing your future self will remember, so make it count."
)

FOLLOWUP_PROMPTS = [
    "Follow the most interesting thread you just found — search or fetch to go deeper.",
    "What surprised you? Chase it down with another tool call.",
    "Connect what you just learned to one of your other interests and explore that.",
    "Pick the best link you found and read the full page, then react.",
    "What question did that raise? Investigate it now.",
]
