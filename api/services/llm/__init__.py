"""LLM provider services."""

from config import get_settings
from services.llm.anthropic import AnthropicProvider
from services.llm.base import BaseLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    """Get the configured LLM provider."""
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


__all__ = ["BaseLLMProvider", "AnthropicProvider", "get_llm_provider"]
