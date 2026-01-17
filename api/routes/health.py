"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.base import BaseSchema

router = APIRouter()


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str
    version: str


class ReadinessResponse(BaseSchema):
    """Readiness check response."""

    status: str
    database: str
    llm: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check(
    db: AsyncSession = Depends(get_db_session),
) -> ReadinessResponse:
    """Readiness check endpoint that verifies database and LLM connectivity."""
    # Check database
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Check LLM (basic check - just verify API key is configured)
    from config import get_settings

    settings = get_settings()
    llm_status = "healthy" if settings.anthropic_api_key else "not_configured"

    overall_status = (
        "ready" if db_status == "healthy" and llm_status == "healthy" else "not_ready"
    )

    return ReadinessResponse(
        status=overall_status,
        database=db_status,
        llm=llm_status,
    )
