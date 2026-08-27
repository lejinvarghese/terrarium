"""System prompts, composed from context rather than baked into personas.

Three independent layers, assembled per call:

  identity   who the agent is - temperament, interests, voice. Always present.
             Names no tools and no people, so it travels anywhere.
  task       what it is doing right now: a daily exploration, or a conversation.
  delivery   where its output goes - Telegram, a Discord channel, or nowhere.
             Appended only when there is somewhere for a finding to land.

`compose()` is the only way a system prompt is built. Adding a surface means
adding a delivery block, not editing three personas.
"""

from src.landscapes.undergrowth.incubator.config import (
    CONVERSATION_BRIEF,
    DELIVERY_DISCORD,
    DELIVERY_TELEGRAM,
    LANDSCAPE_INSTRUCTIONS,
    TOOL_INSTRUCTIONS,
)

EXPLORE = "explore"
CHAT = "chat"

DELIVERY = {
    "telegram": DELIVERY_TELEGRAM,
    "discord": DELIVERY_DISCORD,
    None: "",
}


def _task_layer(cfg: dict, task: str) -> list[str]:
    """How the agent should be working right now."""
    if task == EXPLORE:
        return [cfg["drive"], LANDSCAPE_INSTRUCTIONS, TOOL_INSTRUCTIONS]
    return [CONVERSATION_BRIEF]


def compose(cfg: dict, task: str = CHAT, delivery: str | None = None, extra: str = "") -> str:
    """Build one agent's system prompt for one context.

    Args:
        cfg: the agent's persona config
        task: EXPLORE for a daily episode, CHAT for a conversation
        delivery: "telegram", "discord", or None when the reply is the output
        extra: anything context-specific, e.g. who else is in the room
    """
    layers = [cfg["identity"], *_task_layer(cfg, task), DELIVERY.get(delivery, ""), extra]
    return "\n\n".join(layer.strip() for layer in layers if layer and layer.strip())
