"""Shared persona presentation - emoji and colour per agent, used by every portal."""

PERSONA_EMOJIS = {
    "anya": "🎨",
    "casper": "🪴",
    "cassia": "📅",
    "freya": "💪",
    "nigella": "🍳",
    "nyx": "🚀",
    "pepper": "🌶️",
    "sage": "📚",
    "system": "🌿",
    "default": "🤖",
}

# Discord embed / webhook accent colours
PERSONA_COLORS = {
    "anya": 0xE91E63,
    "casper": 0x2ECC71,
    "cassia": 0xF1C40F,
    "freya": 0xE74C3C,
    "nigella": 0xD35400,
    "nyx": 0x9B59B6,
    "pepper": 0xFF6B35,
    "sage": 0x3498DB,
    "system": 0x1ABC9C,
    "default": 0x95A5A6,
}


def emoji(persona: str | None) -> str:
    """Emoji for a persona, falling back to the default bot glyph."""
    return PERSONA_EMOJIS.get((persona or "default").lower(), PERSONA_EMOJIS["default"])


def color(persona: str | None) -> int:
    """Accent colour for a persona, falling back to grey."""
    return PERSONA_COLORS.get((persona or "default").lower(), PERSONA_COLORS["default"])


def display_name(persona: str | None) -> str:
    """Emoji-prefixed title, e.g. "🚀 Nyx"."""
    name = (persona or "casper").title()
    return f"{emoji(persona)} {name}"
