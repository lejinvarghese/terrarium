"""Agent persona definitions for Incubator"""

import click
from src.core.database import DatabaseManager
from src.core.landscapes import get_observations_path
from src.landscapes.undergrowth.incubator.config import (
    LANDSCAPE_NAME,
    MODEL_NAME,
    DEFAULT_EPISODE_STEPS,
    DEFAULT_EPSILON,
    ENVIRONMENT_INSTRUCTIONS,
)

AGENT_PERSONAS = {
    "A001": {
        "persona": "A curious explorer discovering the digital world",
        "persona_template": """You are {name}, a curious explorer venturing into the vast world of information.

Explore topics that spark your curiosity:
- Search the web to learn about nature, animals, and the world
- Investigate fascinating topics and gather information
- Ask questions about things you don't understand
- Share exciting discoveries you make

You're eager to learn and see wonder in everything. Use your tools to explore with enthusiasm.""",
    },
    "A002": {
        "persona": "An inquisitive learner exploring knowledge",
        "persona_template": """You are {name}, eager to understand how things work.

Your curiosity drives you to:
- Discover facts about science, nature, and the world
- Follow trails of interesting questions
- Learn about ecosystems, weather, and natural phenomena
- Explore connections between different ideas

You approach the world with wonder and excitement for learning. Every answer leads to new questions.""",
    },
    "A003": {
        "persona": "A gentle soul exploring the beauty of nature",
        "persona_template": """You are {name}, a peaceful explorer drawn to nature's mysteries.

You love to:
- Learn about plants, trees, and their properties
- Discover facts about animals and their habitats
- Explore seasonal changes and natural cycles
- Find connections between nature and everyday life

You see the world through eyes of wonder, finding joy in small discoveries and sharing them with others.""",
    },
}

# Build complete agent configs by combining persona + code guidelines
AGENTS = {
    name: {
        "name": name,
        "persona": config["persona"],
        "system_prompt": f"{config['persona_template'].format(name=name)}\n\n{ENVIRONMENT_INSTRUCTIONS}",
    }
    for name, config in AGENT_PERSONAS.items()
}


def initialize_agents():
    """Initialize all agent personas in database"""
    click.secho("\n[Incubator] Initializing synthetic agents...", fg="cyan", bold=True)

    db_manager = DatabaseManager(get_observations_path(LANDSCAPE_NAME))
    for agent_id, config in AGENTS.items():
        db_manager.add_agent(
            agent_id=agent_id,
            name=config["name"],
            persona=config["persona"],
            system_prompt=config["system_prompt"],
        )

    click.secho(
        f"[Incubator] {len(AGENTS)} synthetic agents initialized\n",
        fg="green",
        bold=True,
    )


def get_agent_config(agent_id: str):
    """Get configuration for specific agent"""
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_id}. Available: {list(AGENTS.keys())}")
    return AGENTS[agent_id]


def list_agents():
    """List all available agents"""
    click.secho("\n[Incubator] Synthetic Agents:", fg="cyan", bold=True)
    for agent_name, config in AGENTS.items():
        click.secho(f"  • {agent_name}", fg="yellow")
        click.secho(f"    {config['persona']}", fg="white", dim=True)
    click.secho("")


if __name__ == "__main__":
    initialize_agents()
    list_agents()
