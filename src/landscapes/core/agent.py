import asyncio
import re

import click
from agno.agent import Agent
from agno.models.ollama import Ollama

from src.core.models import ModelFactory
from src.landscapes.core.constants import (
    DATABASE,
    DEFAULT_AGENT_ID,
    DEFAULT_AGENT_NAME,
    DEFAULT_COLORS,
    DEFAULT_INSTRUCTIONS,
    DEFAULT_MODEL_NAME,
    DEFAULT_USER_ID,
)
from src.landscapes.core.tools import display_tools, get_tools


def remove_thinking_tags(
    run_output,
) -> str:
    """Remove thinking tags."""
    return re.sub(r"^.*</think>\s*", "", run_output.content, flags=re.DOTALL)


class BaseAgent:
    """
    Base class for an agent.

    Supports multiple model backends:
    - ollama: Local models via Ollama
    - openrouter: API models via OpenRouter (e.g., Grok)
    """

    def __init__(
        self,
        id: str = DEFAULT_AGENT_ID,
        name: str = DEFAULT_AGENT_NAME,
        user_id: str = DEFAULT_USER_ID,
        instructions: str = DEFAULT_INSTRUCTIONS,
        model_name: str = DEFAULT_MODEL_NAME,
        model_type: str = "ollama",
        debug: bool = False,
        skip_logging: bool = True,
    ):
        self._id = id
        self._name = name
        self._user_id = user_id
        self._instructions = instructions
        self._model_name = model_name
        self._model_type = model_type
        self._debug = debug
        self._db = DATABASE if not skip_logging else None
        self._model = self._create_model()
        self._tools = None
        self._agent = None

    @classmethod
    async def create(cls, **kwargs):
        """Async factory method to create an instance of BaseAgent."""
        instance = cls(**kwargs)
        instance._tools = [await get_tools()]
        instance._agent = instance._create_agent()
        display_tools(instance._tools[0])
        return instance

    async def close(self):
        """Clean up MCP connections. Should be called when done with the agent."""
        if self._tools:
            await self._tools[0].close()

    def _create_model(self):
        """Create a model instance based on model_type.

        Supports:
        - ollama: Local models
        - openrouter: API models (Grok, Claude, etc.)
        """
        if self._model_type == "ollama":
            return Ollama(
                id=self._model_name,
                options={
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 20,
                    "repeat_penalty": 1.0,
                    "num_ctx": 4096,
                },
            )
        elif self._model_type == "openrouter":
            return ModelFactory.create_openrouter(
                model_id=self._model_name,
                temperature=0.7,
                max_tokens=4096,
            )
        else:
            raise ValueError(
                f"Unknown model_type: {self._model_type}. " "Supported: ollama, openrouter"
            )

    def _create_agent(self):
        """Create an agent instance."""
        return Agent(
            id=self._id,
            name=self._name,
            model=self._model,
            user_id=self._user_id,
            db=self._db,
            markdown=True,
            instructions=self._instructions,
            # tools
            compress_tool_results=False,
            tools=self._tools,
            tool_call_limit=10,
            # state
            enable_agentic_state=True,
            enable_agentic_memory=True,
            enable_user_memories=True,
            # session
            add_session_state_to_context=True,
            add_session_summary_to_context=True,
            add_memories_to_context=True,
            search_session_history=True,
            cache_session=True,
            enable_session_summaries=True,
            # history
            add_history_to_context=True,
            num_history_sessions=5,
            read_chat_history=True,
            # events
            store_events=True,
            debug_mode=self._debug,
            debug_level=2,
            post_hooks=[remove_thinking_tags],
        )

    @property
    def id(self) -> str:
        """The unique identifier for the agent."""
        return self._id

    @property
    def name(self) -> str:
        """The name of the agent."""
        return self._name

    @property
    def instructions(self) -> str:
        """The instructions for the agent."""
        return self._instructions

    async def run(self, instruction: str, **kwargs):
        """Execute the agent's logic.

        Returns:
            RunResponse object from agno
        """
        response = await self._agent.arun(instruction, **kwargs)
        return response


async def run_agent(task: str, debug: bool, skip_logging: bool):
    """Async logic for running the agent."""
    agent = await BaseAgent.create(debug=debug, skip_logging=skip_logging)
    try:
        response = await agent.run(task)
        attributes = [
            "run_id",
            "agent_id",
            "agent_name",
            "session_id",
            "user_id",
            "content",
            "events",
        ]
        for i, (k, v) in enumerate(response.items()):
            if k not in attributes:
                continue
            click.secho(f"{k}: {v}", fg=DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
    finally:
        await agent.close()


@click.command()
@click.option(
    "-t",
    "--task",
    type=str,
    required=True,
    default="What is the best value of humanity, and why?",
)
@click.option("-d", "--debug", type=bool, required=False, is_flag=True, default=False)
@click.option("-s", "--skip-logging", type=bool, required=False, is_flag=True, default=False)
def main(task: str, debug: bool, skip_logging: bool):
    asyncio.run(run_agent(task, debug, skip_logging))


if __name__ == "__main__":
    main()
