"""Core infrastructure for Terrarium agent system"""

from src.core.agents import AgentRegistry
from src.core.models import ModelFactory
from src.core.goals import GoalGenerator

__all__ = ["AgentRegistry", "ModelFactory", "GoalGenerator"]
