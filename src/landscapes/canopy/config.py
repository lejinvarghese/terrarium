"""Configuration for The Canopy landscape"""

from pathlib import Path

# Landscape identity
LANDSCAPE_NAME = "canopy"
LANDSCAPE_CULTURE = """
The Canopy is a realm of elevated intelligence and strategic foresight.
Agents here operate from a birds-eye view, recognizing patterns across time and domains.
They are self-improving, learning from every task, and building wisdom through reflection.

This is not reactive intelligence - it is proactive, contemplative, synthesizing.
Agents generate their own tasks based on context, execute strategically, and improve autonomously.
"""

# Model configuration
MODEL_NAME = "llama3.2:latest"  # Local model for autonomous operation
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"  # For complex reasoning tasks

# Task generation intervals
DEFAULT_TASK_GEN_INTERVAL_MINUTES = 30  # Generate new tasks every 30min
MIN_TASK_PRIORITY = 0.3  # Don't execute tasks below this priority

# Self-reflection thresholds
PATTERN_PROMOTION_THRESHOLD = 3  # Uses in 7 days to promote WARM -> HOT
PATTERN_ARCHIVE_DAYS = 90  # Days without use to demote to COLD
MAX_HOT_PATTERNS = 10  # Maximum patterns in HOT tier

# Memory paths
LANDSCAPE_PATH = Path(__file__).parent
MEMORY_PATH = LANDSCAPE_PATH / "memory"
HOT_MEMORY_DB = MEMORY_PATH / "hot.db"
WARM_MEMORY_DB = MEMORY_PATH / "warm.db"
COLD_MEMORY_DB = MEMORY_PATH / "cold.db"

# Telegram bot (Casper)
TELEGRAM_AGENT_ID = "casper"
TELEGRAM_PREFIX = "[Canopy]"  # Messages prefixed with landscape

# Available MCP tools
AVAILABLE_TOOLS = [
    # Calendar & scheduling
    "mcp__google-calendar__list-events",
    "mcp__google-calendar__create-event",
    "mcp__google-calendar__get-current-time",
    # Web research
    "mcp__tavily__tavily-search",
    "mcp__tavily__tavily-extract",
    # Knowledge
    "mcp__arxiv__search_papers",
    "mcp__arxiv__download_paper",
    # Communication
    "mcp__terrarium__send_telegram_message",
    # Weather (for context)
    "mcp__openweathermap__get-current-weather",
]

# Bot personas (simple registry)
BOT_PERSONAS = {
    "oracle": {
        "name": "Oracle",
        "role": "Strategic foresight and pattern recognition",
        "focus": ["long-term planning", "trend analysis", "future scenarios"],
    },
    "chronicler": {
        "name": "Chronicler",
        "role": "Memory keeper and knowledge synthesizer",
        "focus": ["pattern extraction", "memory management", "wisdom archiving"],
    },
    "athena": {
        "name": "Athena",
        "role": "Tactical execution and decision support",
        "focus": ["meeting prep", "task execution", "strategic actions"],
    },
}
