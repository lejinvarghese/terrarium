"""Dynamic goal generation for agent exploration based on persona and interests"""

import random


class GoalGenerator:
    """Generate exploration goals based on agent persona and interests."""

    # Goal templates by archetype
    ARCHETYPE_TEMPLATES = {
        "accelerationist": [
            "Find the latest arxiv papers on {topic} from 2025",
            "Search for recent breakthroughs in {topic}",
            "Explore emerging trends in {topic}",
            "Investigate new developments in {topic} research",
            "Discover cutting-edge applications of {topic}",
        ],
        "creative": [
            "Discover new {topic} music or artists",
            "Search for innovative {topic} techniques",
            "Explore experimental {topic} styles",
            "Find inspiring {topic} examples",
            "Investigate emerging {topic} trends",
        ],
        "philosopher": [
            "Search for papers connecting {topic} with other fields",
            "Explore philosophical aspects of {topic}",
            "Find interdisciplinary research on {topic}",
            "Investigate timeless questions about {topic}",
            "Discover deep insights about {topic}",
        ],
        "researcher": [
            "Search for recent research on {topic}",
            "Explore current developments in {topic}",
            "Find papers or articles about {topic}",
            "Investigate new methods in {topic}",
            "Discover applications of {topic}",
        ],
    }

    def __init__(self, epsilon: float = 0.2):
        """Initialize goal generator.

        Args:
            epsilon: Exploration rate (0.0 = pure exploitation, 1.0 = pure exploration)
                    Controls whether to focus on known interests vs try new things
        """
        self.epsilon = epsilon

    def generate(
        self, agent_config: dict, recent_memories: list = None, epsilon: float = None
    ) -> str:
        """Generate a goal for the agent based on persona and memories.

        Args:
            agent_config: Agent configuration with archetype, interests, etc.
            recent_memories: Recent memories to inform goal (future use)
            epsilon: Override default exploration rate

        Returns:
            Goal string suitable for agent prompt
        """
        eps = epsilon if epsilon is not None else self.epsilon

        archetype = agent_config.get("archetype", "researcher")
        interests = agent_config.get("interests", ["general topics"])

        # Decide: exploration or exploitation
        if random.random() < eps:
            # Exploration: try something tangential or new
            goal = self._generate_exploratory_goal(archetype, interests)
        else:
            # Exploitation: deepen known interests
            goal = self._generate_focused_goal(archetype, interests)

        return goal

    def _generate_focused_goal(self, archetype: str, interests: list[str]) -> str:
        """Generate goal focused on known interests.

        Args:
            archetype: Agent archetype
            interests: List of agent's interest topics

        Returns:
            Goal string
        """
        # Pick a random interest
        topic = random.choice(interests)

        # Get templates for this archetype
        templates = self.ARCHETYPE_TEMPLATES.get(archetype, self.ARCHETYPE_TEMPLATES["researcher"])

        # Pick a random template and fill in the topic
        template = random.choice(templates)
        return template.format(topic=topic)

    def _generate_exploratory_goal(self, archetype: str, interests: list[str]) -> str:
        """Generate goal that explores new territory.

        For now, this is similar to focused goals but could later:
        - Combine multiple interests
        - Try adjacent topics
        - Follow trending topics

        Args:
            archetype: Agent archetype
            interests: List of agent's interest topics

        Returns:
            Goal string
        """
        # For exploration, try combining topics or use broader terms
        if len(interests) > 1 and random.random() < 0.5:
            # Combine two interests
            topic1, topic2 = random.sample(interests, 2)
            topic = f"{topic1} and {topic2}"
        else:
            topic = random.choice(interests)

        templates = self.ARCHETYPE_TEMPLATES.get(archetype, self.ARCHETYPE_TEMPLATES["researcher"])

        template = random.choice(templates)
        return template.format(topic=topic)
