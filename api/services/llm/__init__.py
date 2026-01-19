"""LLM provider services."""

from config import get_settings
from services.llm.anthropic import AnthropicProvider
from services.llm.base import BaseLLMProvider
from services.llm.gemini import GeminiProvider


def get_llm_provider() -> BaseLLMProvider:
    """Get the configured LLM provider."""
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        return AnthropicProvider()
    elif settings.llm_provider == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


__all__ = ["BaseLLMProvider", "AnthropicProvider", "GeminiProvider", "get_llm_provider"]
