"""Configuration for The Undergrowth incubator"""

# Landscape identity
LANDSCAPE_NAME = "undergrowth"
LANDSCAPE_DISPLAY_NAME = "The Undergrowth"
LANDSCAPE_DESCRIPTION = "Dark, gothic, emergent, underground intelligence"

# Model configuration
MODEL_NAME = "qwen3:1.7b"

# Exploration defaults
DEFAULT_EPISODE_STEPS = 10
DEFAULT_EPSILON = 0.2  # 20% random exploration

# Training (future use)
LORA_RANK = 8
LORA_ALPHA = 16
LEARNING_RATE = 2e-4

# Environment instructions
ENVIRONMENT_INSTRUCTIONS = """
Use the tools available to you to explore and learn. Think step by step about what information you need.
You can call multiple tools in sequence to build up knowledge.
"""
