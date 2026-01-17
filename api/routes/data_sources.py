"""Data source management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from core.exceptions import DataSourceConnectionError, DataSourceNotFoundError
from models.data_source import DataSource
from schemas.data_source import (
    DataSourceCreate,
    DataSourceListResponse,
    DataSourceResponse,
    DataSourceTestResponse,
    DataSourceUpdate,
    SchemaInfo,
)
from services.data.connectors import get_connector

router = APIRouter()


def _to_response(data_source: DataSource) -> DataSourceResponse:
    """Convert DataSource model to response schema."""
    schema_info = None
    if data_source.schema_info:
        schema_info = SchemaInfo(**data_source.schema_info)

    return DataSourceResponse(
        id=data_source.id,
        name=data_source.name,
        description=data_source.description,
        source_type=data_source.source_type,
        schema_info=schema_info,
        is_active=data_source.is_active,
        created_at=data_source.created_at,
        updated_at=data_source.updated_at,
    )


@router.post("/data-sources", response_model=DataSourceResponse, status_code=201)
async def create_data_source(
    request: DataSourceCreate,
    db: AsyncSession = Depends(get_db_session),
) -> DataSourceResponse:
    """Create a new data source."""
    data_source = DataSource(
        name=request.name,
        description=request.description,
        source_type=request.source_type,
        connection_config=request.connection_config.model_dump(exclude_none=True),
    )

    db.add(data_source)
    await db.flush()
    await db.refresh(data_source)

    return _to_response(data_source)


@router.get("/data-sources", response_model=DataSourceListResponse)
async def list_data_sources(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db_session),
) -> DataSourceListResponse:
    """List all data sources."""
    stmt = select(DataSource)
    if active_only:
        stmt = stmt.where(DataSource.is_active == True)  # noqa: E712
    stmt = stmt.order_by(DataSource.created_at.desc())

    result = await db.execute(stmt)
    data_sources = result.scalars().all()

    return DataSourceListResponse(
        items=[_to_response(ds) for ds in data_sources],
        total=len(data_sources),
    )


@router.get("/data-sources/{data_source_id}", response_model=DataSourceResponse)
async def get_data_source(
    data_source_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> DataSourceResponse:
    """Get a specific data source by ID."""
    stmt = select(DataSource).where(DataSource.id == data_source_id)
    result = await db.execute(stmt)
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    return _to_response(data_source)


@router.patch("/data-sources/{data_source_id}", response_model=DataSourceResponse)
async def update_data_source(
    data_source_id: str,
    request: DataSourceUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> DataSourceResponse:
    """Update a data source."""
    stmt = select(DataSource).where(DataSource.id == data_source_id)
    result = await db.execute(stmt)
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    update_data = request.model_dump(exclude_unset=True)
    if "connection_config" in update_data and update_data["connection_config"]:
        update_data["connection_config"] = update_data["connection_config"].model_dump(
            exclude_none=True
        )

    for field, value in update_data.items():
        setattr(data_source, field, value)

    await db.flush()
    await db.refresh(data_source)

    return _to_response(data_source)


@router.delete("/data-sources/{data_source_id}", status_code=204)
async def delete_data_source(
    data_source_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a data source."""
    stmt = select(DataSource).where(DataSource.id == data_source_id)
    result = await db.execute(stmt)
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    await db.delete(data_source)


@router.post(
    "/data-sources/{data_source_id}/test", response_model=DataSourceTestResponse
)
async def test_data_source_connection(
    data_source_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> DataSourceTestResponse:
    """Test connection to a data source and retrieve schema info."""
    stmt = select(DataSource).where(DataSource.id == data_source_id)
    result = await db.execute(stmt)
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        connector = get_connector(
            source_type=data_source.source_type,
            connection_config=data_source.connection_config,
        )
        schema_info = await connector.get_schema()

        # Update cached schema info
        data_source.schema_info = schema_info.model_dump()
        await db.flush()

        return DataSourceTestResponse(
            success=True,
            message="Connection successful",
            schema_info=schema_info,
        )

    except DataSourceNotFoundError as e:
        return DataSourceTestResponse(
            success=False,
            message=str(e),
        )
    except DataSourceConnectionError as e:
        return DataSourceTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )
    except Exception as e:
        return DataSourceTestResponse(
            success=False,
            message=f"Unexpected error: {str(e)}",
        )
