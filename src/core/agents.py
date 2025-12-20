"""Base agent classes for landscape agent management"""

import click
from src.core.database import DatabaseManager
from src.core.landscapes import get_observations_path


class Agent:
    """Single agent with persona configuration"""

    def __init__(self, agent_id: str, persona: str, persona_template: str):
        self.agent_id = agent_id
        self.persona = persona
        self.system_prompt = f"{persona_template.format(name=agent_id)}\n".strip()

    def to_dict(self):
        return {"name": self.agent_id, "persona": self.persona, "system_prompt": self.system_prompt}


class AgentRegistry:
    """Manages collection of agents"""

    def __init__(self, landscape_name: str, agent_personas: dict):
        """
        Args:
            landscape_name: Name of the landscape
            agent_personas: Dict of {agent_id: {"persona": str, "persona_template": str}}
        """
        self.landscape_name = landscape_name
        self.observations_db = DatabaseManager(get_observations_path(landscape_name))
        self.agents = {
            agent_id: Agent(agent_id, config["persona"], config["persona_template"])
            for agent_id, config in agent_personas.items()
        }

        # Check if agents already exist in database
        session = self.observations_db.get_session()
        from src.core.database import Agent as AgentModel
        existing_agents = {a.agent_id for a in session.query(AgentModel).all()}
        session.close()

        new_agents = set(self.agents.keys()) - existing_agents

        if new_agents:
            click.secho(f"\n[{landscape_name.title()}] Initializing {len(new_agents)} new agents...", fg="cyan", bold=True)

        for agent in self.agents.values():
            config = agent.to_dict()
            self.observations_db.add_agent(agent.agent_id, config["name"], agent.persona, config["system_prompt"])

        if new_agents:
            click.secho(f"[{landscape_name.title()}] ✓ Agents initialized\n", fg="green")

    def get(self, agent_id: str) -> Agent:
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}. Available: {list(self.agents.keys())}")
        return self.agents[agent_id]

    def get_config(self, agent_id: str) -> dict:
        return self.get(agent_id).to_dict()

    def display(self):
        """Display all agents"""
        click.secho(f"\n[{self.landscape_name.title()}] Agents:", fg="cyan", bold=True)
        for agent in self.agents.values():
            click.secho(f"  • {agent.agent_id}", fg="yellow")
            click.secho(f"    {agent.persona}", fg="white", dim=True)
