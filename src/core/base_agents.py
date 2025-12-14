"""Base agent classes for landscape agent management"""

import click
from src.core.database import DatabaseManager


class Agent:
    """Single agent with persona configuration"""

    def __init__(self, agent_id: str, persona: str, persona_template: str, env_instructions: str = ""):
        self.agent_id = agent_id
        self.persona = persona
        self.system_prompt = f"{persona_template.format(name=agent_id)}\n\n{env_instructions}".strip()

    def to_dict(self):
        return {"name": self.agent_id, "persona": self.persona, "system_prompt": self.system_prompt}


class AgentRegistry:
    """Manages collection of agents"""

    def __init__(self, landscape_name: str, agent_personas: dict, env_instructions: str, db_manager: DatabaseManager):
        """
        Args:
            landscape_name: Name of the landscape
            agent_personas: Dict of {agent_id: {"persona": str, "persona_template": str}}
            env_instructions: Environment instructions to append to all agents
            db_manager: Database manager instance
        """
        self.landscape_name = landscape_name
        self.db_manager = db_manager

        # Build Agent instances
        self.agents = {
            agent_id: Agent(agent_id, config["persona"], config["persona_template"], env_instructions)
            for agent_id, config in agent_personas.items()
        }

        # Initialize in database
        click.secho(f"\n[{landscape_name.title()}] Initializing {len(self.agents)} agents...", fg="cyan", bold=True)
        for agent in self.agents.values():
            config = agent.to_dict()
            db_manager.add_agent(agent.agent_id, config["name"], agent.persona, config["system_prompt"])
        click.secho(f"[{landscape_name.title()}] ✓ Agents initialized\n", fg="green")

    def get(self, agent_id: str) -> Agent:
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}. Available: {list(self.agents.keys())}")
        return self.agents[agent_id]

    def get_config(self, agent_id: str) -> dict:
        return self.get(agent_id).to_dict()

    def list(self):
        """Display all agents"""
        click.secho(f"\n[{self.landscape_name.title()}] Agents:", fg="cyan", bold=True)
        for agent in self.agents.values():
            click.secho(f"  • {agent.agent_id}", fg="yellow")
            click.secho(f"    {agent.persona}", fg="white", dim=True)
        click.secho("")
