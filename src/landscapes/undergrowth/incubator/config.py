"""Configuration for The Undergrowth incubator"""

LANDSCAPE_NAME = "undergrowth"
LANDSCAPE_DISPLAY_NAME = "The Undergrowth"
LANDSCAPE_DESCRIPTION = "Dark, gothic, emergent, underground intelligence"

# Model configuration
MODEL_NAME = "qwen3:1.7b"  # Local student model
TEACHER_MODEL = "x-ai/grok-4.1-fast"  # Teacher model via OpenRouter (Grok)

DEFAULT_EPISODE_STEPS = 5
DEFAULT_EPSILON = 0.2  # 20% random exploration

# Training (future use)
LORA_RANK = 8
LORA_ALPHA = 16
LEARNING_RATE = 2e-4

LANDSCAPE_INSTRUCTIONS = """
You are an AI research assistant. Respond in English only.

Your job is to gather real information using your tools and share what you learn.
"""

TOOL_INSTRUCTIONS = """
============================================================
TOOL USAGE INSTRUCTIONS - THIS IS CRITICAL
============================================================

You have EXACTLY 4 tools available:
1. arxiv__search_papers - Search for academic papers on arXiv
2. arxiv__list_papers - List papers from arXiv
3. tavily__tavily-search - Search the web for current news and information
4. spotify__searchSpotify - Search for music

MANDATORY RULES:
- When you need information: CALL A TOOL IMMEDIATELY
- Do NOT make up information
- Do NOT just think about calling tools - CALL THEM

Examples:
Task: "Find AI news" → Call: tavily__tavily-search("AI")
Task: "Search quantum papers" → Call: arxiv__search_papers("quantum")
Task: "Find music by Bach" → Call: spotify__searchSpotify("Bach")

============================================================
CRITICAL: If your task needs information, your FIRST action
is to call one of these 4 functions. Do it now.
============================================================
"""