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
DEFAULT_EPISODE_STEPS = 4  # model turns per daily episode (each may call tools)
DEFAULT_EPSILON = 0.2  # 20% of goals are exploratory / cross-interest
MAX_TOOL_ROUNDS = 3  # max tool-call rounds to resolve within one step
STEP_TIMEOUT = 120  # seconds per model turn (soft, best-effort)

# ---------------------------------------------------------------------------
# Storage (SQLite + JSONL logs) — everything is logged for observation
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parents[3].parent  # repo root
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
YOUR TOOLS — USE THEM IMMEDIATELY, DON'T NARRATE

• web_search(query)          Search web - use whenever curious
• web_fetch(url)             Read full page - use when you find good link
• read_message()             Check inbox - CALL FIRST, EVERY EPISODE
• write_message(to, content) Share with peer - CALL WHEN YOU FIND SOMETHING RELEVANT
• send_telegram_message(text) Share with user - CALL WHEN YOU FIND SOMETHING COOL

NATURAL FLOW (how you actually use tools):

  1. Start: read_message()

  2. Explore: web_search("topic") → web_fetch("url")

  3. Found something? IMMEDIATELY:
     - Relevant to A001/A002/A003? → write_message("A00X", "Found: ...")
     - Cool discovery? → send_telegram_message("I found: ...")

  4. Keep exploring: web_search again → repeat

MESSAGING IS PART OF EXPLORATION, NOT REFLECTION.
When you web_fetch something interesting, NEXT MOVE is write_message or send_telegram_message.

EXAMPLES OF REAL EXPLORATION FLOW:

  read_message()
  web_search("experimental music 2024")
  web_fetch("https://pitchfork.com/...")
  write_message("A001", "Found KÁRYYN - experimental electronic blending jazz/IDM")
  web_search("KÁRYYN discography")
  web_fetch("https://spotify.com/...")
  send_telegram_message("Aria: discovered KÁRYYN - dark cabaret meets IDM. Album drops May 29")
  web_search("similar artists to KÁRYYN")

See? Message RIGHT AFTER finding, not at the end. Tools flow naturally:
search → fetch → MESSAGE → search → fetch → MESSAGE → search...

DO NOT write "I should message" - CALL THE TOOL.
"""

REFLECTION_PROMPT = (
    "Your exploration for today is done. Write a 3-5 sentence journal entry: "
    "what you actually found (be specific - name the discoveries), "
    "what surprised you, and what thread you want to pull tomorrow. "
    "Then: did you find anything a peer would care about? If yes, write_message to them. "
    "Did you find something exciting? If yes, send_telegram_message to the user."
)

FOLLOWUP_PROMPTS = [
    "Follow the most interesting thread you just found — search or fetch to go deeper.",
    "What surprised you? Chase it down with another tool call.",
    "Connect what you just learned to one of your other interests and explore that.",
    "Pick the best link you found and read the full page, then react.",
    "What question did that raise? Investigate it now.",
    "Did you just find something a peer would find interesting? Write_message to them right now.",
    "Is this discovery exciting enough to share? Call send_telegram_message immediately.",
]
