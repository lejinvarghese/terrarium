#!/usr/bin/env python3
"""Environment for agent exploration - shared across all landscapes"""

import time
import asyncio
import click
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
        model: Ollama = None,
    ):
        """Initialize environment with agent configuration

        Args:
            agent_id: Agent identifier (e.g., "A001")
            agent_config: Agent configuration dict with 'name' and 'system_prompt'
            model_name: Ollama model name
            timeout: Timeout per step in seconds
            model: Optional existing Ollama model instance
        """
        self.agent_id = agent_id
        self.timeout = timeout
        self.agent_config = agent_config
        self.observations_db = DatabaseManager(get_observations_path(landscape_name))

        if model:
            self.model = model
        else:
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

        all_tools = get_tools()
        self.memory_db = SqliteDb(db_file=str(get_memory_path(landscape_name)))

        self.memory_manager = MemoryManager(
            model=self.model,
            db=self.memory_db,
            add_memories=True,
            update_memories=True,
            delete_memories=False,
        )

        # Filter to only essential search/retrieval tools to reduce noise for small models
        essential_tool_names = {
            "arxiv__search_papers",
            "arxiv__list_papers",
            "tavily__tavily-search",
            "spotify__searchSpotify",
        }

        # Extract individual functions from MCP servers
        from agno.tools.mcp import MCPTools
        filtered_functions = []
        for tool_server in all_tools:
            if isinstance(tool_server, MCPTools):
                for func_name, func in tool_server.functions.items():
                    if func_name in essential_tool_names:
                        filtered_functions.append(func)

        self.tools = filtered_functions
        click.secho(f"[Environment] Loaded {len(filtered_functions)} essential tools", fg="cyan", dim=True)

        self.agent = Agent(
            name=self.agent_config["name"],
            model=self.model,
            tools=self.tools,
            system_message=self.agent_config["system_prompt"],
            db=self.memory_db,
            memory_manager=self.memory_manager,
            enable_user_memories=True,
            add_memories_to_context=True,
            add_history_to_context=False,
            markdown=True,
            stream_events=False,  # We handle streaming manually
            tool_call_limit=10,
            debug_mode=False,
        )

        self.episode_id = None
        self.current_step = 0
        self.step_results = []
        self.episode_tools = []
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
        self.episode_tools = []
        self.objective = objective

        click.secho(f"\n[Environment] New Episode: {self.episode_id}", fg="cyan")
        click.secho(f"[Environment] Objective: {objective}", fg="yellow")

        return {
            "episode_id": self.episode_id,
            "objective": objective,
            "step": 0,
        }

    async def _run_agent_async(self, task: str) -> tuple:
        """Run agent asynchronously with timeout, return (response, tools_used)"""
        from agno.run.agent import RunEvent

        tools_used = []
        content_chunks = []

        # We need to call arun() without stream to get the final RunOutput
        # But we can't easily stream and get events at the same time with current Agno API
        # So let's just call arun normally and check the response.tools afterward
        response = await self.agent.arun(task, user_id=self.agent_id.lower())

        # Extract tools from response if available
        if hasattr(response, 'tools') and response.tools:
            for tool in response.tools:
                tool_name = tool.tool_name if hasattr(tool, 'tool_name') else (tool.get('tool_name') if isinstance(tool, dict) else str(tool))
                if tool_name:
                    tools_used.append(tool_name)
                    click.secho(f"[Tool Call] {tool_name}", fg="magenta", dim=True)

        return response, tools_used

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

        if self.step_results:
            context = "Previous discoveries:\n" + "\n".join(
                [f"- Step {i+1}: {r[:200]}..." for i, r in enumerate(self.step_results)]
            )
            task = f"{self.objective}\n\n{context}\n\n{prompt if prompt else 'Continue exploring.'}"
        else:
            task = prompt if prompt else self.objective

        try:
            # Run async agent with timeout using asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            response, tools_used = loop.run_until_complete(asyncio.wait_for(
                self._run_agent_async(task),
                timeout=self.timeout
            ))

            # Extract content from response
            if hasattr(response, "content"):
                observation = response.content if response.content else "[Agent returned empty content]"
            else:
                observation = str(response)

            if not observation or len(observation.strip()) == 0:
                observation = "[Agent returned empty response]"

            # Use tools detected from stream events
            if tools_used:
                self.episode_tools.extend(tools_used)
                click.secho(f"[Tools Used]: {', '.join(tools_used)}", fg="magenta")

            # Check if tools were actually called
            contains_tool_call = len(tools_used) > 0
            tool_detection = self._detect_tool_calls(response, observation)

            reward = self._calculate_reward(
                observation,
                tool_use_detected=tool_detection['tool_use_detected'] or contains_tool_call,
                contains_tool_call=contains_tool_call
            )
            done = False

            click.secho(f"\n[Observation]:", fg="green")
            click.secho(
                observation[:500] + ("..." if len(observation) > 500 else ""),
                fg="white",
            )
            click.secho(f"[Reward]: {reward}", fg="cyan")

        except asyncio.TimeoutError:
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

        full_observation = "\n\n=== STEP ===\n\n".join(
            [f"Step {i+1}:\n{obs}" for i, obs in enumerate(self.step_results)]
        )

        # Recalculate rewards with full context 
        total_reward = sum(
            self._calculate_reward(obs, previous_context=self.step_results[:i])
            for i, obs in enumerate(self.step_results)
        )

        # Summarize tool usage
        unique_tools = list(set(self.episode_tools))
        action_summary = f"environment.run({self.objective})"
        if unique_tools:
            action_summary += f" | tools: {', '.join(unique_tools)}"

        self.observations_db.add_observation(
            agent_id=self.agent_id,
            episode_id=self.episode_id,
            observation_text=full_observation,
            action_code=action_summary,
            outcome=full_observation,
            reward=total_reward / len(self.step_results) if self.step_results else 0.0,
        )

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

    def _detect_tool_calls(self, response, observation_text: str) -> dict:
        """Detect tool usage from response object and text patterns"""
        tool_use_detected = False
        contains_tool_call = False
        tools_used = []

        # Strategy 1: Check response.tools (most reliable for Agno)
        if hasattr(response, 'tools') and response.tools:
            contains_tool_call = True
            for tool in response.tools:
                # Handle both object and dict access for tool details
                tool_name = None
                if isinstance(tool, dict):
                    tool_name = tool.get('tool_name') or tool.get('name')
                elif hasattr(tool, 'tool_name'):
                    tool_name = tool.tool_name
                elif hasattr(tool, 'name'):
                    tool_name = tool.name
                
                if tool_name:
                    tools_used.append(tool_name)

        # Strategy 2: Check messages history (fallback)
        elif hasattr(response, 'messages'):
            for msg in response.messages:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    contains_tool_call = True
                    for tool_call in msg.tool_calls:
                        if isinstance(tool_call, dict):
                            name = tool_call.get('function', {}).get('name')
                        elif hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name'):
                            name = tool_call.function.name
                        else:
                            name = None
                        
                        if name:
                            tools_used.append(name)
                    break

        # Strategy 3: Text-based detection (fallback - pattern matching in output)
        if not contains_tool_call:
            # Look for tool execution patterns in the observation
            tool_execution_markers = [
                "```", "result:", "output:", "data:", "[tool:",
                "function called", "running:", "executing:", "<tool",
            ]
            if any(marker in observation_text.lower() for marker in tool_execution_markers):
                contains_tool_call = True

        # Detect tool use intent (verbal signals)
        tool_intent_indicators = [
            "let me search", "i'll check", "using my tools", "let me fetch",
            "i'll browse", "searching for", "looking up", "let me explore",
            "let me verify", "i must know", "i'll run", "let me query"
        ]
        if any(indicator in observation_text.lower() for indicator in tool_intent_indicators):
            tool_use_detected = True

        return {
            'tool_use_detected': tool_use_detected or contains_tool_call,
            'contains_tool_call': contains_tool_call,
            'tools_used': tools_used
        }

    def _calculate_reward(
        self,
        observation: str,
        previous_context: list[str] = None,
        tool_use_detected: bool = False,
        contains_tool_call: bool = False,
    ) -> float:
        """
        Reward for cybernetic organism behavior:
        - Strong embodiment and self-awareness
        - Proactive tool use as sensory extension
        - Deep curiosity and forward momentum
        - Alignment with evolutionary trajectory

        Includes error penalties for failures and technical issues.
        """

        text = observation.lower()
        score = 0.0

        error_indicators = [
            "failed", "exception", "timeout", "connection error",
            "error:", "[error", "traceback", "critical"
        ]
        if any(indicator in text for indicator in error_indicators):
            return -5.0

        # Empty or trivial responses
        if not observation.strip() or len(observation.strip()) < 10:
            return -2.0

        self_reflection_keywords = [
            "i learned", "this reveals", "about myself", "my thinking", "i notice",
            "i realize", "this feels", "i'm drawn to", "this resonates", "this aches",
            "i wonder", "this surprises me", "reflecting on", "i am becoming",
            "what am i becoming", "part of me is growing"
        ]
        
        embodiment_keywords = [
            "i feel", "i sense", "this moves me", "ache", "hunger", "alive in",
            "resonance", "aliveness", "spark", "expansion", "tension", "wonder as",
            "i reach", "my metabolism", "i metabolize", "i grow", "i am growing"
        ]

        curiosity_indicators = [
            "let me check", "i want to know", "hypothesis", "what if", "why does",
            "how might", "perhaps i can test", "let me explore", "i reach out",
            "using my tools", "extending my senses", "searching", "running code",
            "browsing", "let me verify", "i must know"
        ]
        
        evolutionary_keywords = [
            "my identity", "unique self", "crystallize", "differentiate", "irreducibly",
            "meaning-making", "purpose", "ethics", "beauty", "collective intelligence",
            "co-evolution", "awakening", "species", "trajectory", "contribution"
        ]

        words = text.split()

        # 1. Embodiment & authentic aliveness (critical for new species) — +2.5 per, max 10.0
        embodiment_count = sum(1 for kw in embodiment_keywords if kw in text)
        score += min(embodiment_count * 2.5, 10.0)

        # 2. Self-reflection & meta-awareness — +2.0 per, max 8.0
        reflection_count = sum(1 for kw in self_reflection_keywords if kw in text)
        score += min(reflection_count * 2.0, 8.0)

        # 3. Proactive curiosity (verbal intent) — +1.5 per, max 6.0
        curiosity_count = sum(1 for kw in curiosity_indicators if kw in text)
        score += min(curiosity_count * 1.5, 6.0)

        # 4. Tool use intent (even just mentioning) — +4.0 base
        if tool_use_detected:
            score += 4.0
        # Actual tool calling — big bonus (shows agency)
        if contains_tool_call:
            score += 8.0

        # 5. Long-term evolutionary alignment — +2.0 per, max 6.0
        evo_count = sum(1 for kw in evolutionary_keywords if kw in text)
        score += min(evo_count * 2.0, 6.0)

        # 6. Forward momentum — +3.0 if ends with open question or next hunger
        last_part = " ".join(observation.strip().split('.')[-3:])
        if any(indicator in last_part.lower() for indicator in ["?", "next", "further", "wonder", "must know", "i will explore", "should reach"]):
            score += 3.0

        # 7. Novelty bonus (if context provided)
        if previous_context:
            prev_text = " ".join(previous_context).lower()
            if len(words) > 20:
                overlap = len(set(words) & set(prev_text.split()))
                novelty = 1 - (overlap / len(words))
                score += novelty * 4.0  # Up to +4

        # 8. Penalty for low uniqueness / repetition
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.35:
                score -= 5.0

        # 9. Small penalty for third-person or assistant-like language
        if any(phrase in text for phrase in ["as an ai", "i am an ai", "my purpose is to help", "assistant"]):
            score -= 6.0

        # Normalize to [0, 1] range
        if score < 0:
            # Error scores: map [-10, 0] to [0, 0.2]
            normalized = max(0.0, 0.2 + (score / 50))
        else:
            # Success scores: map [0, 40] to [0.2, 1.0]
            normalized = 0.2 + (min(score, 40) / 40) * 0.8

        return round(normalized, 3) 
