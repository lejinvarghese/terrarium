from typing import Any


class BaseEnvironment:
    """
    Base class for an Environment.
    """

    async def reset(self, **kwargs) -> Any:
        """Resets the environment and returns the initial observation."""
        pass

    async def step(self, action: Any) -> tuple[Any, float, bool, dict[str, Any]]:
        """
        Run one timestep of the environment's dynamics.
        Returns: (observation, reward, done, info)
        """
        pass

    def close(self) -> None:
        """Perform any necessary cleanup."""
        pass
