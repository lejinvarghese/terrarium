import asyncio
import click

from agno.agent import Agent
from agno.models.ollama import Ollama



class BaseAgent:
    """
    Base class for an agent.
    """

    def __init__(
        self,
        id: str,
        name: str,
        instructions: str,
        model_name: str,
        debug: bool,
    ):
        self._id = id
        self._name = name
        self._instructions = instructions
        self._model_name = model_name
        self._debug = debug
        self._model = self._create_model()
        self._agent = self._create_agent()

    def _create_model(self):
        """Create a model instance."""
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

    def _create_agent(self):
        """Create an agent instance."""
        return Agent(
            id=self._id,
            name=self._name,
            model=self._model,
            markdown=True,
            system_message=self._instructions,
            # tools
            compress_tool_results=True,
            tools=[],
            tool_call_limit=5,
            # state
            enable_agentic_state=True,
            enable_agentic_memory=True,
            # session
            add_session_state_to_context=True,
            search_session_history=True,
            cache_session=True,
            enable_session_summaries=True,
            add_session_summary_to_context=True,
            # history
            add_history_to_context=True,
            num_history_sessions=5,
            # events
            store_events=True,
            debug_mode=self._debug,
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

    async def run(self, instruction: str, **kwargs) -> str:
        """Execute the agent's logic."""
        response = await self._agent.arun(instruction, **kwargs)
        return response.to_dict()


async def run_agent(task: str, debug: bool):
    """Async logic for running the agent."""
    agent = BaseAgent(
        id="1",
        name="Agent 1",
        instructions="You are a helpful assistant.",
        model_name="qwen3:1.7b",
        debug=debug,
    )
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
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]
    for i, (k, v) in enumerate(response.items()):
        if k not in attributes:
            continue
        click.secho(f"{k}: {v}", fg=colors[i % len(colors)])


@click.command()
@click.option(
    "--task",
    type=str,
    required=True,
    default="What is the best value of humanity, and why?",
)
@click.option("--debug", type=bool, required=False, default=False)
def main(task: str, debug: bool):
    asyncio.run(run_agent(task, debug))


if __name__ == "__main__":
    main()
