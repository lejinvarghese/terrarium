"""Agent persona definitions"""

from src.core.agents import AgentRegistry
from src.landscapes.undergrowth.incubator.config import (
    LANDSCAPE_NAME,
    TOOL_INSTRUCTIONS,
    LANDSCAPE_INSTRUCTIONS,
)

AGENT_PERSONAS = {
    "A001": {
        "persona": "Research assistant",
        "persona_template": f"""
You are {{name}}, a research assistant.

{LANDSCAPE_INSTRUCTIONS}

{TOOL_INSTRUCTIONS}
""",
    },
    "A002": {
        "persona": "Research assistant",
        "persona_template": f"""
You are {{name}}, a research assistant.

{LANDSCAPE_INSTRUCTIONS}

{TOOL_INSTRUCTIONS}
""",
    },
    "A003": {
        "persona": "Research assistant",
        "persona_template": f"""
You are {{name}}, a research assistant.

{LANDSCAPE_INSTRUCTIONS}

{TOOL_INSTRUCTIONS}
""",
    },
}


class LandscapeAgentRegistry(AgentRegistry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


agent_registry = LandscapeAgentRegistry(LANDSCAPE_NAME, AGENT_PERSONAS)
