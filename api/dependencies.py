"""Dependency injection for FastAPI routes."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from core.database import get_db_session
from services.llm import BaseLLMProvider, get_llm_provider

# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]

# Database session dependency
DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


# LLM provider dependency
async def get_llm() -> AsyncGenerator[BaseLLMProvider, None]:
    """Get LLM provider instance."""
    provider = get_llm_provider()
    yield provider


LLMProviderDep = Annotated[BaseLLMProvider, Depends(get_llm)]
