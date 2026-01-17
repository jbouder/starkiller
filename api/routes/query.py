"""Query processing endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db_session
from core.exceptions import QueryException
from models.query import Query
from schemas.query import (
    QueryHistoryItem,
    QueryHistoryResponse,
    QueryRequest,
    QueryResponse,
    QueryResultData,
)
from schemas.visualization import VisualizationResponse
from services.query.executor import QueryExecutor

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db_session),
) -> QueryResponse:
    """Process a natural language query and return results with visualization."""
    executor = QueryExecutor(db)

    try:
        query = await executor.execute(
            natural_language_query=request.query,
            data_source_id=request.data_source_id,
        )

        # Build response
        result_data = None
        if query.result_data:
            result_data = QueryResultData(
                columns=query.result_data.get("columns", []),
                rows=query.result_data.get("rows", []),
                row_count=query.result_data.get("row_count", 0),
            )

        visualization = None
        if query.visualization:
            visualization = VisualizationResponse(
                id=query.visualization.id,
                title=query.visualization.title,
                description=query.visualization.description,
                chart_type=query.visualization.chart_type,
                chart_config=query.visualization.chart_config,
                data_config=query.visualization.data_config,
                is_saved=query.visualization.is_saved,
                query_id=query.visualization.query_id,
                created_at=query.visualization.created_at,
                updated_at=query.visualization.updated_at,
            )

        return QueryResponse(
            id=query.id,
            natural_language_query=query.natural_language_query,
            generated_query=query.generated_query,
            query_type=query.query_type,
            status=query.status,
            result_data=result_data,
            error_message=query.error_message,
            execution_time_ms=query.execution_time_ms,
            data_source_id=query.data_source_id,
            visualization=visualization,
            created_at=query.created_at,
            updated_at=query.updated_at,
        )

    except QueryException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/query/history", response_model=QueryHistoryResponse)
async def get_query_history(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db_session),
) -> QueryHistoryResponse:
    """Get query history with pagination."""
    offset = (page - 1) * page_size

    # Get total count
    count_stmt = select(Query)
    result = await db.execute(count_stmt)
    total = len(result.scalars().all())

    # Get paginated queries
    stmt = (
        select(Query)
        .options(selectinload(Query.visualization))
        .order_by(Query.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    queries = result.scalars().all()

    items = [
        QueryHistoryItem(
            id=q.id,
            natural_language_query=q.natural_language_query,
            status=q.status,
            created_at=q.created_at,
            execution_time_ms=q.execution_time_ms,
        )
        for q in queries
    ]

    return QueryHistoryResponse(items=items, total=total)


@router.get("/query/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> QueryResponse:
    """Get a specific query by ID."""
    stmt = (
        select(Query)
        .options(selectinload(Query.visualization))
        .where(Query.id == query_id)
    )
    result = await db.execute(stmt)
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    result_data = None
    if query.result_data:
        result_data = QueryResultData(
            columns=query.result_data.get("columns", []),
            rows=query.result_data.get("rows", []),
            row_count=query.result_data.get("row_count", 0),
        )

    visualization = None
    if query.visualization:
        visualization = VisualizationResponse(
            id=query.visualization.id,
            title=query.visualization.title,
            description=query.visualization.description,
            chart_type=query.visualization.chart_type,
            chart_config=query.visualization.chart_config,
            data_config=query.visualization.data_config,
            is_saved=query.visualization.is_saved,
            query_id=query.visualization.query_id,
            created_at=query.visualization.created_at,
            updated_at=query.visualization.updated_at,
        )

    return QueryResponse(
        id=query.id,
        natural_language_query=query.natural_language_query,
        generated_query=query.generated_query,
        query_type=query.query_type,
        status=query.status,
        result_data=result_data,
        error_message=query.error_message,
        execution_time_ms=query.execution_time_ms,
        data_source_id=query.data_source_id,
        visualization=visualization,
        created_at=query.created_at,
        updated_at=query.updated_at,
    )
