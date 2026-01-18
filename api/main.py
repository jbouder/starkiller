"""FastAPI application entry point for Starkiller API."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from core.database import init_db
from core.logging import setup_logging
from routes import dashboards, data_sources, health, query

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Starkiller API",
        description="Generative BI tool that transforms natural language queries into data visualizations",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
    app.include_router(query.router, prefix=settings.api_v1_prefix, tags=["Query"])
    app.include_router(
        data_sources.router, prefix=settings.api_v1_prefix, tags=["Data Sources"]
    )
    app.include_router(
        dashboards.router, prefix=settings.api_v1_prefix, tags=["Dashboards"]
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
