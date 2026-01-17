"""Query execution orchestration service."""

import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import QueryException
from core.logging import get_logger
from models.data_source import DataSource
from models.query import Query
from models.visualization import Visualization
from services.data.connectors import get_connector
from services.data.processor import DataProcessor
from services.llm import get_llm_provider
from services.visualization.generator import VisualizationGenerator

logger = get_logger(__name__)


class QueryExecutor:
    """Orchestrates the query execution pipeline."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.llm = get_llm_provider()
        self.processor = DataProcessor()
        self.viz_generator = VisualizationGenerator()

    async def execute(
        self,
        natural_language_query: str,
        data_source_id: str | None = None,
    ) -> Query:
        """
        Execute a natural language query end-to-end.

        This method:
        1. Creates a Query record
        2. Gets the data source and schema
        3. Uses LLM to generate pandas code
        4. Executes the code against the data
        5. Uses LLM to recommend visualization
        6. Saves the visualization

        Args:
            natural_language_query: The user's question in natural language
            data_source_id: Optional data source ID to query

        Returns:
            Query model with results and visualization
        """
        start_time = time.time()

        # Create query record
        query = Query(
            natural_language_query=natural_language_query,
            status="processing",
            data_source_id=data_source_id,
        )
        self.db.add(query)
        await self.db.flush()

        try:
            # Get data source
            data_source = await self._get_data_source(data_source_id)

            # Get connector and schema
            connector = get_connector(
                source_type=data_source.source_type,
                connection_config=data_source.connection_config,
            )

            async with connector:
                schema_info = await connector.get_schema()

                # Generate query using LLM
                llm_response = await self.llm.generate_query(
                    natural_language=natural_language_query,
                    schema_info=schema_info.model_dump(),
                )

                query.generated_query = llm_response.get("query", "")
                query.query_type = llm_response.get("query_type", "pandas")

                # Execute the generated code
                result_df = await connector.execute_query(query.generated_query)

                # Convert to response format
                query.result_data = self.processor.dataframe_to_dict(result_df)

            # Generate visualization recommendation
            if query.result_data and query.result_data.get("rows"):
                viz_config = await self._generate_visualization(
                    query_id=query.id,
                    result_data=query.result_data,
                    natural_language_query=natural_language_query,
                )

                if viz_config:
                    visualization = Visualization(
                        title=viz_config.get("title", "Query Result"),
                        description=viz_config.get("description"),
                        chart_type=viz_config.get("chart_type", "bar"),
                        chart_config=viz_config.get("chart_config", {}),
                        data_config={},
                        query_id=query.id,
                    )
                    self.db.add(visualization)

            # Mark as completed
            query.status = "completed"
            query.execution_time_ms = int((time.time() - start_time) * 1000)

            await self.db.flush()
            await self.db.refresh(query)

            return query

        except Exception as e:
            logger.error("Query execution failed", error=str(e), query_id=query.id)
            query.status = "failed"
            query.error_message = str(e)
            query.execution_time_ms = int((time.time() - start_time) * 1000)
            await self.db.flush()
            raise QueryException(f"Query execution failed: {str(e)}")

    async def _get_data_source(self, data_source_id: str | None) -> DataSource:
        """Get data source by ID or return the first active one."""
        if data_source_id:
            stmt = select(DataSource).where(DataSource.id == data_source_id)
        else:
            stmt = (
                select(DataSource)
                .where(DataSource.is_active == True)  # noqa: E712
                .order_by(DataSource.created_at.desc())
                .limit(1)
            )

        result = await self.db.execute(stmt)
        data_source = result.scalar_one_or_none()

        if not data_source:
            raise QueryException("No data source available")

        return data_source

    async def _generate_visualization(
        self,
        query_id: str,
        result_data: dict[str, Any],
        natural_language_query: str,
    ) -> dict[str, Any] | None:
        """Generate visualization recommendation for query results."""
        try:
            viz_response = await self.llm.recommend_visualization(
                query_result=result_data,
                natural_language=natural_language_query,
            )
            return viz_response
        except Exception as e:
            logger.warning(
                "Failed to generate visualization",
                error=str(e),
                query_id=query_id,
            )
            return None
