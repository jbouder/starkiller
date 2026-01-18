"""Dashboard management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db_session
from core.exceptions import GenerationException
from models.dashboard import Dashboard
from models.data_source import DataSource
from schemas.dashboard import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
)
from schemas.data_source import DataSourceResponse, SchemaInfo
from schemas.generation import GenerateRequest, GenerateResponse
from services.generation import DashboardGenerationOrchestrator

router = APIRouter()


def _to_response(dashboard: Dashboard) -> DashboardResponse:
    """Convert Dashboard model to response schema."""
    data_sources = []
    for ds in dashboard.data_sources:
        schema_info = None
        if ds.schema_info:
            schema_info = SchemaInfo(**ds.schema_info)
        
        data_sources.append(
            DataSourceResponse(
                id=ds.id,
                name=ds.name,
                description=ds.description,
                source_type=ds.source_type,
                schema_info=schema_info,
                is_active=ds.is_active,
                created_at=ds.created_at,
                updated_at=ds.updated_at,
            )
        )

    return DashboardResponse(
        id=dashboard.id,
        title=dashboard.title,
        description=dashboard.description,
        data_sources=data_sources,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
    )


async def _get_data_sources_by_ids(
    session: AsyncSession, data_source_ids: list[str]
) -> list[DataSource]:
    """Fetch data sources by IDs."""
    if not data_source_ids:
        return []

    stmt = select(DataSource).where(DataSource.id.in_(data_source_ids))
    result = await session.execute(stmt)
    data_sources = result.scalars().all()

    if len(data_sources) != len(data_source_ids):
        found_ids = {ds.id for ds in data_sources}
        missing_ids = set(data_source_ids) - found_ids
        raise HTTPException(
            status_code=400,
            detail=f"Data sources not found: {', '.join(missing_ids)}",
        )

    return list(data_sources)


@router.post("/dashboards", response_model=DashboardResponse, status_code=201)
async def create_dashboard(
    request: DashboardCreate,
    db: AsyncSession = Depends(get_db_session),
) -> DashboardResponse:
    """Create a new dashboard."""
    data_sources = await _get_data_sources_by_ids(db, request.data_source_ids)

    dashboard = Dashboard(
        title=request.title,
        description=request.description,
        data_sources=data_sources,
    )

    db.add(dashboard)
    await db.flush()
    await db.refresh(dashboard)

    return _to_response(dashboard)


@router.get("/dashboards", response_model=list[DashboardResponse])
async def list_dashboards(
    db: AsyncSession = Depends(get_db_session),
) -> list[DashboardResponse]:
    """List all dashboards."""
    stmt = (
        select(Dashboard)
        .options(selectinload(Dashboard.data_sources))
        .order_by(Dashboard.created_at.desc())
    )
    result = await db.execute(stmt)
    dashboards = result.scalars().all()

    return [_to_response(d) for d in dashboards]


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> DashboardResponse:
    """Get a specific dashboard by ID."""
    stmt = (
        select(Dashboard)
        .options(selectinload(Dashboard.data_sources))
        .where(Dashboard.id == dashboard_id)
    )
    result = await db.execute(stmt)
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return _to_response(dashboard)


@router.patch("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: str,
    request: DashboardUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> DashboardResponse:
    """Update a dashboard."""
    stmt = (
        select(Dashboard)
        .options(selectinload(Dashboard.data_sources))
        .where(Dashboard.id == dashboard_id)
    )
    result = await db.execute(stmt)
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    update_data = request.model_dump(exclude_unset=True)
    
    # Handle relationships
    if "data_source_ids" in update_data:
        data_source_ids = update_data.pop("data_source_ids")
        if data_source_ids is not None:
             dashboard.data_sources = await _get_data_sources_by_ids(db, data_source_ids)

    for field, value in update_data.items():
        setattr(dashboard, field, value)

    await db.flush()
    await db.refresh(dashboard)

    return _to_response(dashboard)


@router.delete("/dashboards/{dashboard_id}", status_code=204)
async def delete_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a dashboard."""
    stmt = select(Dashboard).where(Dashboard.id == dashboard_id)
    result = await db.execute(stmt)
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    await db.delete(dashboard)


@router.post("/dashboards/{dashboard_id}/generate", response_model=GenerateResponse)
async def generate_dashboard(
    dashboard_id: str,
    request: GenerateRequest | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> GenerateResponse:
    """
    Generate React visualization code for a dashboard.

    This endpoint uses LLM to:
    1. Analyze the dashboard's associated data sources
    2. Generate appropriate data queries
    3. Create React/Recharts visualization code

    The optional request body can include:
    - query: Natural language query to customize the visualization
    - visualization_preferences: Chart types, color scheme, layout preferences
    """
    orchestrator = DashboardGenerationOrchestrator(db)

    try:
        return await orchestrator.generate(dashboard_id, request)
    except GenerationException as e:
        raise HTTPException(
            status_code=400,
            detail={"error": e.__class__.__name__, "message": e.message, "details": e.details},
        )
