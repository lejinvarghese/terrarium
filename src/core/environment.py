#!/usr/bin/env python3
"""Environment for agent exploration - shared across all landscapes"""

import time
import click
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager

from src.core.database import DatabaseManager
from src.core.tools import get_tools
from src.core.landscapes import get_observations_path, get_memory_path


class Environment:
    """Environment for agent exploration

    Terminology:
    - Episode: Full exploration session with multiple steps
    - Step: Single iteration where agent takes action and receives reward
    - State: Agent's accumulated knowledge and context
    """

    def __init__(
        self,
        agent_id: str,
        agent_config: dict,
        model_name: str,
        landscape_name: str,
        timeout: int = 180,
    ):
        """Initialize environment with agent configuration

        Args:
            agent_id: Agent identifier (e.g., "A001")
            agent_config: Agent configuration dict with 'name' and 'system_prompt'
            model_name: Ollama model name
            timeout: Timeout per step in seconds
        """
        self.agent_id = agent_id
        self.timeout = timeout
        self.agent_config = agent_config
        self.observations_db = DatabaseManager(get_observations_path(landscape_name))

        # Initialize model
        self.model = Ollama(
            id=model_name,
            options={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 20,
                "repeat_penalty": 1.0,
                "num_ctx": 4096,
            },
        )

        self.tools = get_tools()
        self.memory_db = SqliteDb(db_file=str(get_memory_path(landscape_name)))

        self.memory_manager = MemoryManager(
            model=self.model,
            db=self.memory_db,
            add_memories=True,
            update_memories=True,
            delete_memories=False,
        )

        self.agent = Agent(
            name=self.agent_config["name"],
            model=self.model,
            tools=self.tools,
            instructions=self.agent_config["system_prompt"],
            db=self.memory_db,
            memory_manager=self.memory_manager,
            enable_user_memories=True,
            add_memories_to_context=True,
            add_history_to_context=False,
            markdown=True,
            stream_events=True,
            tool_call_limit=5,
            debug_mode=False,
        )

        # Episode state
        self.episode_id = None
        self.current_step = 0
        self.step_results = []
        self.objective = None

    def reset(self, objective: str) -> dict:
        """Reset environment for new episode

        Args:
            objective: Initial exploration objective

        Returns:
            Initial state observation
        """
        self.episode_id = f"{self.agent_id}_{int(time.time())}"
        self.current_step = 0
        self.step_results = []
        self.objective = objective

        click.secho(f"\n[Environment] New Episode: {self.episode_id}", fg="cyan")
        click.secho(f"[Environment] Objective: {objective}", fg="yellow")

        return {
            "episode_id": self.episode_id,
            "objective": objective,
            "step": 0,
        }

    def step(self, prompt: str = None) -> dict:
        """Execute one environment step

        Args:
            prompt: Optional guidance for this step (defaults to objective)

        Returns:
            Step result with observation, reward, done flag
        """
        self.current_step += 1

        click.secho(f"\n{'='*60}", fg="cyan")
        click.secho(f"Step {self.current_step}", fg="cyan", bold=True)
        click.secho(f"{'='*60}", fg="cyan")

        # Build context from previous steps
        if self.step_results:
            context = "Previous discoveries:\n" + "\n".join(
                [f"- Step {i+1}: {r[:200]}..." for i, r in enumerate(self.step_results)]
            )
            task = f"{self.objective}\n\n{context}\n\n{prompt if prompt else 'Continue exploring.'}"
        else:
            task = prompt if prompt else self.objective

        # Execute agent action with timeout
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self.agent.run,
                    task,
                    user_id=self.agent_id.lower(),
                )
                response = future.result(timeout=self.timeout)

            observation = response.content if hasattr(response, "content") and response.content else str(response)

            if not observation or len(observation.strip()) == 0:
                observation = "[Agent returned empty response]"

            reward = self._calculate_reward(observation)
            done = False

            click.secho(f"\n[Observation]:", fg="green")
            click.secho(
                observation[:500] + ("..." if len(observation) > 500 else ""),
                fg="white",
            )
            click.secho(f"[Reward]: {reward}", fg="cyan")

        except FuturesTimeoutError:
            observation = f"[Step timed out after {self.timeout}s]"
            reward = -0.5
            done = False

            click.secho(f"\n[TIMEOUT]: Step exceeded {self.timeout}s", fg="red", bold=True)

        except Exception as e:
            observation = f"[Error: {str(e)}]"
            reward = -0.5
            done = False

            click.secho(f"\n[ERROR]: {e}", fg="red", bold=True)

        self.step_results.append(observation)

        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "step": self.current_step,
            "episode_id": self.episode_id,
        }

    def close(self) -> dict:
        """Close episode and store final observation

        Returns:
            Episode summary with total reward
        """
        if not self.episode_id:
            return {"message": "No active episode"}

        # Combine all observations
        full_observation = "\n\n=== STEP ===\n\n".join(
            [f"Step {i+1}:\n{obs}" for i, obs in enumerate(self.step_results)]
        )

        total_reward = sum(self._calculate_reward(obs) for obs in self.step_results)

        # Store in database
        self.observations_db.add_observation(
            agent_id=self.agent_id,
            episode_id=self.episode_id,
            observation_text=full_observation,
            action_code=f"environment.run({self.objective})",
            outcome=full_observation,
            reward=total_reward / len(self.step_results) if self.step_results else 0.0,
        )

        # Get memories created (use same user_id as in step execution)
        memories = self.agent.get_user_memories(user_id=self.agent_id.lower())
        if memories:
            click.secho(f"\n[Memory] Created {len(memories)} memories total", fg="cyan")
            for i, mem in enumerate(memories[:5], 1):
                click.secho(f"  {i}. {mem.memory}", fg="white")
            if len(memories) > 5:
                click.secho(f"  ... and {len(memories) - 5} more", fg="white", dim=True)

        click.secho(f"\n[Environment] Episode Complete!", fg="green", bold=True)
        click.secho(f"  Total Steps: {self.current_step}", fg="white")
        click.secho(f"  Avg Reward: {total_reward / len(self.step_results):.2f}", fg="white")

        return {
            "episode_id": self.episode_id,
            "total_steps": self.current_step,
            "total_reward": total_reward,
            "avg_reward": (total_reward / len(self.step_results) if self.step_results else 0.0),
        }

    def _calculate_reward(self, observation: str) -> float:
        """Calculate reward based on observation quality"""
        obs_lower = observation.lower()

        if any(x in obs_lower for x in ["failed", "exception", "timeout", "connection error"]):
            return -0.3
        if any(x in obs_lower for x in ["found", "discovered", "learned"]):
            return 0.7
        if len(observation) > 300:
            return 0.7

        return 0.5
