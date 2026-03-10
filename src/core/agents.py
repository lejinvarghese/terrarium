"""Agent registry for managing agent personas across landscapes"""


class AgentRegistry:
    """Registry for managing agent personas in a landscape.

    Attributes:
        landscape_name: Name of the landscape (e.g., "undergrowth")
        agents: Dictionary of agent_id -> agent_config
    """

    def __init__(self, landscape_name: str, agent_personas: dict):
        """Initialize registry with landscape name and agent personas.

        Args:
            landscape_name: Name of the landscape
            agent_personas: Dict of agent_id -> config with keys:
                - name: Agent display name
                - archetype: Agent type (e.g., "accelerationist", "creative")
                - interests: List of topics agent is interested in
                - preferred_tools: List of MCP tool names
                - persona_template: System prompt template
        """
        self.landscape_name = landscape_name
        self.agents = agent_personas

    def get_config(self, agent_id: str) -> dict:
        """Get full configuration for an agent.

        Args:
            agent_id: Agent identifier (e.g., "A001")

        Returns:
            Agent configuration dict with added metadata

        Raises:
            ValueError: If agent_id not found in registry
        """
        if agent_id not in self.agents:
            available = ", ".join(self.agents.keys())
            raise ValueError(f"Unknown agent: {agent_id}. Available: {available}")

        # Copy config and add metadata
        config = self.agents[agent_id].copy()
        config["id"] = agent_id
        config["landscape"] = self.landscape_name

        return config

    def list_agents(self) -> list[str]:
        """Get list of all agent IDs in this registry."""
        return list(self.agents.keys())

    def get_agent_by_name(self, name: str) -> str | None:
        """Get agent ID by display name.

        Args:
            name: Agent display name (e.g., "Nyx")

        Returns:
            Agent ID if found, None otherwise
        """
        for agent_id, config in self.agents.items():
            if config.get("name", "").lower() == name.lower():
                return agent_id
        return None
