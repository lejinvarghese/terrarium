"""Shared memory configuration for Terrarium."""

import os
from pathlib import Path

from dotenv import load_dotenv
from mem0 import Memory
from mem0.configs.base import EmbedderConfig, MemoryConfig
from mem0.vector_stores.configs import VectorStoreConfig

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Memory configuration
MEMORY_VECTOR_PATH = os.getenv("MEMORY_VECTOR_PATH", "data/memory_vectors")
SCHEDULER_USER_ID = os.getenv("SCHEDULER_USER_ID", "terrarium_system")  # Legacy, not used
USER_ID = os.getenv("TELEGRAM_CHAT_ID")
DANIELLE_USER_ID = os.getenv("DANIELLE_TELEGRAM_CHAT_ID")

# Custom prompts optimized for selective memory storage
CUSTOM_FACT_EXTRACTION_PROMPT = """
Extract and store only significant, actionable, or reference-worthy information. Focus on facts that provide lasting value for future conversations.

STORE these categories:
- Personal preferences, decisions, and commitments
- Work goals, projects, technical insights, and learnings
- Health and fitness progress, goals, and routines
- Important plans, events, and time-sensitive information
- Specific facts about interests, hobbies, and values
- Behavioral patterns and productivity insights
- Relationship details and social commitments

IGNORE these patterns:
- Greetings, small talk, acknowledgments ("hi", "thanks", "okay")
- Simple queries with transactional responses (weather, time, calculations)
- Speculation without commitment ("might", "maybe", "I think", "possibly")
- Information already clearly stored in memory
- Bot capabilities or feature discussions
- Temporary context that won't be useful later

Examples:

Input: Hi! How are you today?
Output: {"facts": []}

Input: What's the weather like tomorrow?
Output: {"facts": []}

Input: I might try going to the gym next week.
Output: {"facts": []}

Input: I've decided to start going to the gym 4 times a week, focusing on strength training.
Output: {"facts": ["Committed to gym 4x per week with strength training focus"]}

Input: I just finished reading Cryptonomicon and loved it. Next I'm starting Gödel, Escher, Bach.
Output: {"facts": ["Finished reading Cryptonomicon (enjoyed it)", "Starting Gödel, Escher, Bach next"]}

Input: I need to prepare a presentation on reinforcement learning for next Friday's team meeting.
Output: {"facts": ["Presenting on reinforcement learning at team meeting next Friday"]}

Return facts in JSON format as shown above. Be selective - only capture information worth remembering long-term.
"""

CUSTOM_UPDATE_MEMORY_PROMPT = """
You manage memory for an AI assistant. Compare new facts with existing memories and decide:

ADD - New information not already stored
UPDATE - Changes to existing information (keep ID, update content)
DELETE - Contradictory or outdated information
NONE - Already stored or not worth storing

Guidelines:
- Prefer UPDATE over ADD when refining existing facts
- DELETE outdated information (old goals, completed tasks, changed preferences)
- Be aggressive with NONE for redundant or low-value information
- Preserve context in UPDATEs (e.g., "Updated goal from X to Y")

Output format:
{
  "memory": [
    {
      "id": "<existing_id or new>",
      "text": "<memory content>",
      "event": "ADD|UPDATE|DELETE|NONE",
      "old_memory": "<previous content if UPDATE>"
    }
  ]
}
"""


def get_memory():
    """Get configured Memory instance with shared configuration.

    Returns:
        Memory: Configured mem0 Memory instance
    """
    config = MemoryConfig(
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "host": "localhost",
                "port": 6333,
            },
        ),
        embedder=EmbedderConfig(provider="openai", config={"model": "text-embedding-3-small"}),
        custom_fact_extraction_prompt=CUSTOM_FACT_EXTRACTION_PROMPT,
        custom_update_memory_prompt=CUSTOM_UPDATE_MEMORY_PROMPT,
    )
    return Memory(config=config)
