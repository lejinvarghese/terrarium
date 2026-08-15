"""Model factory for creating different LLM backends (Ollama, OpenRouter, etc.)"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class ModelFactory:
    """Factory for creating different model instances."""

    @staticmethod
    def create_ollama(model_id: str, **kwargs) -> Any:
        """Create an Ollama model instance.

        Args:
            model_id: Ollama model identifier (e.g., "qwen3:1.7b")
            **kwargs: Additional model options

        Returns:
            Ollama model instance
        """
        from agno.models.ollama import Ollama

        default_options = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 20,
            "repeat_penalty": 1.0,
            "num_ctx": 4096,
        }

        # Merge with any provided options
        options = {**default_options, **kwargs.get("options", {})}

        return Ollama(
            id=model_id,
            options=options,
        )

    @staticmethod
    def create_openrouter(model_id: str, api_key: str | None = None, **kwargs) -> Any:
        """Create an OpenRouter model instance (via OpenAI-compatible API).

        Args:
            model_id: OpenRouter model identifier (e.g., "x-ai/grok-beta")
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            **kwargs: Additional model options (temperature, max_tokens, etc.)

        Returns:
            OpenAI-compatible model instance configured for OpenRouter
        """
        from agno.models.openai import OpenAIChat

        # Get API key from env if not provided
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenRouter API key not found. Set OPENROUTER_API_KEY "
                    "environment variable or pass api_key parameter."
                )

        return OpenAIChat(
            id=model_id, api_key=api_key, base_url="https://openrouter.ai/api/v1", **kwargs
        )

    @staticmethod
    def create(model_type: str, model_id: str, api_key: str | None = None, **kwargs) -> Any:
        """Create a model instance based on type.

        Args:
            model_type: Type of model ("ollama" or "openrouter")
            model_id: Model identifier
            api_key: API key (for OpenRouter)
            **kwargs: Additional model options

        Returns:
            Model instance

        Raises:
            ValueError: If model_type is unknown
        """
        if model_type == "ollama":
            return ModelFactory.create_ollama(model_id, **kwargs)
        elif model_type == "openrouter":
            return ModelFactory.create_openrouter(model_id, api_key, **kwargs)
        else:
            raise ValueError(
                f"Unknown model type: {model_type}. " "Supported types: ollama, openrouter"
            )
