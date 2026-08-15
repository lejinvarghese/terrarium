"""Core infrastructure for Terrarium agent system"""

from src.core.agents import AgentRegistry
from src.core.goals import GoalGenerator
from src.core.models import ModelFactory

__all__ = ["AgentRegistry", "ModelFactory", "GoalGenerator"]
