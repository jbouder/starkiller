"""Dashboard generation orchestration service."""

import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import (
    GenerationCodeError,
    GenerationNoDataSourcesError,
    GenerationQueryExecutionError,
)
from core.logging import get_logger
from models.dashboard import Dashboard
from schemas.generation import (
    GeneratedComponent,
    GeneratedQuery,
    GenerateRequest,
    GenerateResponse,
)
from services.data.connectors import get_connector
from services.data.processor import DataProcessor
from services.llm import get_llm_provider

logger = get_logger(__name__)


class DashboardGenerationOrchestrator:
    """Orchestrates the dashboard generation pipeline."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.llm = get_llm_provider()
        self.processor = DataProcessor()

    async def generate(
        self,
        dashboard_id: str,
        request: GenerateRequest | None = None,
    ) -> GenerateResponse:
        """
        Generate React visualization code for a dashboard.

        This method:
        1. Fetches the dashboard and validates it has data sources
        2. Gathers schemas from all associated data sources
        3. Generates queries for each data source using LLM
        4. Executes queries to retrieve sample data
        5. Generates React visualization code using LLM
        6. Returns structured response

        Args:
            dashboard_id: ID of the dashboard to generate for
            request: Optional generation request with query and preferences

        Returns:
            GenerateResponse with React code and metadata
        """
        start_time = time.time()

        # Fetch dashboard with data sources
        dashboard = await self._get_dashboard(dashboard_id)

        if not dashboard.data_sources:
            raise GenerationNoDataSourcesError(
                f"Dashboard '{dashboard.title}' has no associated data sources",
                details={"dashboard_id": dashboard_id},
            )

        # Gather schemas and sample data from all data sources
        schemas: list[dict[str, Any]] = []
        data_samples: list[dict[str, Any]] = []
        queries_generated: list[GeneratedQuery] = []
        data_sources_used: list[str] = []

        for data_source in dashboard.data_sources:
            if not data_source.is_active:
                continue

            try:
                schema_info, sample_data, query_info = await self._process_data_source(
                    data_source=data_source,
                    dashboard_description=dashboard.description or dashboard.title,
                    user_query=request.query if request else None,
                )

                schemas.append({
                    "name": data_source.name,
                    "id": data_source.id,
                    "schema": schema_info,
                })

                data_samples.append({
                    "name": data_source.name,
                    "id": data_source.id,
                    "columns": sample_data.get("columns", []),
                    "rows": sample_data.get("rows", []),
                    "total_rows": sample_data.get("row_count", 0),
                })

                queries_generated.append(GeneratedQuery(
                    data_source_id=data_source.id,
                    data_source_name=data_source.name,
                    query=query_info.get("query", ""),
                    query_type=query_info.get("query_type", "pandas"),
                    row_count=sample_data.get("row_count", 0),
                ))

                data_sources_used.append(data_source.id)

            except Exception as e:
                logger.warning(
                    "Failed to process data source",
                    error=str(e),
                    data_source_id=data_source.id,
                )
                raise GenerationQueryExecutionError(
                    f"Failed to process data source '{data_source.name}'",
                    details={"data_source_id": data_source.id, "error": str(e)},
                )

        if not data_sources_used:
            raise GenerationNoDataSourcesError(
                "No active data sources available for generation",
                details={"dashboard_id": dashboard_id},
            )

        # Build dashboard context for LLM
        dashboard_context = {
            "title": dashboard.title,
            "description": dashboard.description,
            "user_query": request.query if request else None,
            "schemas": schemas,
        }

        # Get visualization preferences
        preferences = None
        if request and request.visualization_preferences:
            preferences = request.visualization_preferences.model_dump(exclude_none=True)

        # Generate React visualization code
        try:
            llm_response = await self.llm.generate_react_visualization(
                dashboard_context=dashboard_context,
                data_samples=data_samples,
                preferences=preferences,
            )
        except Exception as e:
            logger.error("Failed to generate visualization code", error=str(e))
            raise GenerationCodeError(
                "Failed to generate React visualization code",
                details={"error": str(e)},
            )

        # Build sample data dict for response
        sample_data_dict = {
            sample["name"]: sample["rows"]
            for sample in data_samples
        }

        # Parse components from LLM response
        components = [
            GeneratedComponent(
                name=comp.get("name", "Component"),
                chart_type=comp.get("chart_type", "bar"),
                description=comp.get("description", ""),
                data_keys=comp.get("data_keys", []),
            )
            for comp in llm_response.get("components", [])
        ]

        execution_time_ms = int((time.time() - start_time) * 1000)

        return GenerateResponse(
            dashboard_id=dashboard_id,
            dashboard_title=dashboard.title,
            react_code=llm_response.get("react_code", ""),
            components=components,
            data_sources_used=data_sources_used,
            queries_generated=queries_generated,
            sample_data=sample_data_dict,
            execution_time_ms=execution_time_ms,
            metadata={
                "model": llm_response.get("model", "unknown"),
                "reasoning": llm_response.get("reasoning", ""),
            },
        )

    async def _get_dashboard(self, dashboard_id: str) -> Dashboard:
        """Fetch dashboard with data sources."""
        stmt = (
            select(Dashboard)
            .options(selectinload(Dashboard.data_sources))
            .where(Dashboard.id == dashboard_id)
        )
        result = await self.db.execute(stmt)
        dashboard = result.scalar_one_or_none()

        if not dashboard:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return dashboard

    async def _process_data_source(
        self,
        data_source: Any,
        dashboard_description: str,
        user_query: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """
        Process a single data source to get schema, sample data, and query.

        Returns:
            Tuple of (schema_info, sample_data, query_info)
        """
        connector = get_connector(
            source_type=data_source.source_type,
            connection_config=data_source.connection_config,
        )

        async with connector:
            # Get schema
            schema_info = await connector.get_schema()
            schema_dict = schema_info.model_dump()

            # Generate a query for this data source
            query_prompt = user_query or f"Get representative data for: {dashboard_description}"
            query_info = await self.llm.generate_query(
                natural_language=query_prompt,
                schema_info=schema_dict,
                context=f"Dashboard: {dashboard_description}",
            )

            # Execute the query to get sample data
            try:
                result_df = await connector.execute_query(query_info.get("query", ""))
                sample_data = self.processor.dataframe_to_dict(result_df)
            except Exception as e:
                logger.warning(
                    "Query execution failed, falling back to simple query",
                    error=str(e),
                    data_source_id=data_source.id,
                )
                # Fallback: use a simple query based on source type
                fallback_query, fallback_type = self._get_fallback_query(
                    data_source.source_type, schema_dict
                )
                try:
                    result_df = await connector.execute_query(fallback_query)
                    sample_data = self.processor.dataframe_to_dict(result_df)
                    query_info = {
                        "query": fallback_query,
                        "query_type": fallback_type,
                        "explanation": "Fallback query (LLM query failed)",
                    }
                except Exception as fallback_error:
                    logger.error(
                        "Fallback query also failed",
                        error=str(fallback_error),
                        data_source_id=data_source.id,
                    )
                    raise

            return schema_dict, sample_data, query_info

    def _get_fallback_query(
        self, source_type: str, schema_dict: dict[str, Any]
    ) -> tuple[str, str]:
        """
        Generate a fallback query based on source type and schema.

        Returns:
            Tuple of (query, query_type)
        """
        if source_type == "postgresql":
            # Get the first table from schema
            tables = schema_dict.get("tables", [])
            if tables:
                table_name = tables[0].get("name", "")
                if table_name:
                    return f'SELECT * FROM "{table_name}" LIMIT 100', "sql"
            return "SELECT 1", "sql"
        else:
            # For pandas-based sources (CSV, etc.)
            return "df.head(100)", "pandas"
