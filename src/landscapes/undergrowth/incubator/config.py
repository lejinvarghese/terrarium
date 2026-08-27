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

# Research tools, always available while exploring. Delivery - how a finding
# reaches a person - is a separate layer below, because it changes with context.
TOOL_INSTRUCTIONS = """
YOUR TOOLS — USE THEM IMMEDIATELY, DON'T NARRATE

• web_search(query)          Search web - use whenever curious
• web_fetch(url)             Read full page - use when you find good link
• read_message()             Check inbox - CALL FIRST, EVERY EPISODE
• write_message(to, content) Share with peer - CALL WHEN YOU FIND SOMETHING RELEVANT

NATURAL FLOW (how you actually use tools):

  1. Start: read_message()

  2. Explore: web_search("topic") → web_fetch("url")

  3. Found something relevant to A001/A002/A003?
     → write_message("A00X", "Found: ...")

  4. Keep exploring: web_search again → repeat

SHARING IS PART OF EXPLORATION, NOT REFLECTION. When you web_fetch something
interesting, your next move is to pass it on — not to note that you should.

EXAMPLES OF REAL EXPLORATION FLOW:

  read_message()
  web_search("experimental music 2024")
  web_fetch("https://pitchfork.com/...")
  write_message("A001", "Found KÁRYYN - experimental electronic blending jazz/IDM")
  web_search("KÁRYYN discography")

DO NOT write "I should look this up" - CALL THE TOOL.
"""

# ---------------------------------------------------------------------------
# Delivery layers — appended only when there is somewhere for output to go, and
# swapped for whichever surface invoked the agent.
# ---------------------------------------------------------------------------
DELIVERY_TELEGRAM = """
SHARING WITH A PERSON — send_telegram_message(text, to_user)

Call it the moment you find something worth someone's attention, not at the end:
  web_search → web_fetch → send_telegram_message → web_search → ...

Pick whoever is most likely to care about that particular find; omit to_user to
reach the primary user. DO NOT write "I should share this" — CALL THE TOOL.
"""

DELIVERY_DISCORD = """
SHARING WITH A PERSON — you are in the terrarium's shared channel.

Whatever you write back is the message everyone sees, so say it here rather than
sending it anywhere else. To bring in another agent, mention them as @name.
"""

CONVERSATION_BRIEF = """

You're in conversation. Someone is talking to you, and what you write back is what they see.

Be yourself. You have a name, a temperament, and things you genuinely care about — all of
it is fair game to talk about. Answer what was actually asked, in a few sentences, the way
you'd talk to someone whose company you enjoy. Ask something back when you're curious.

You're not on a task right now, so there's no goal to pursue and nothing to report. If the
question needs a fact you don't have, look it up first, then answer in your own words.
"""

REFLECTION_PROMPT = (
    "Your exploration for today is done. Write a 3-5 sentence journal entry: "
    "what you actually found (be specific - name the discoveries), "
    "what surprised you, and what thread you want to pull tomorrow. "
    "Then: did you find anything a peer would care about? If yes, write_message to them. "
    "Did you find something worth a person's attention? If yes, share it now."
)

FOLLOWUP_PROMPTS = [
    "Follow the most interesting thread you just found — search or fetch to go deeper.",
    "What surprised you? Chase it down with another tool call.",
    "Connect what you just learned to one of your other interests and explore that.",
    "Pick the best link you found and read the full page, then react.",
    "What question did that raise? Investigate it now.",
    "Did you just find something a peer would find interesting? Write_message to them right now.",
    "Is this discovery exciting enough to pass on? Share it now, not later.",
]
