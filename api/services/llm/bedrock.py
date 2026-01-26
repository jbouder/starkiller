"""AWS Bedrock LLM provider implementation."""

import json
from typing import Any

import aioboto3

from config import get_settings
from core.exceptions import LLMConnectionError, LLMResponseError
from core.logging import get_logger
from services.llm.base import BaseLLMProvider

logger = get_logger(__name__)


class BedrockProvider(BaseLLMProvider):
    """AWS Bedrock implementation for LLM operations using Claude models."""

    def __init__(self) -> None:
        settings = get_settings()
        self.model_id = settings.bedrock_model_id
        self.region = settings.bedrock_region

        # Build session kwargs for credentials
        self.session_kwargs: dict[str, Any] = {}
        if settings.bedrock_access_key_id and settings.bedrock_secret_access_key:
            self.session_kwargs["aws_access_key_id"] = settings.bedrock_access_key_id
            self.session_kwargs["aws_secret_access_key"] = (
                settings.bedrock_secret_access_key
            )
            if settings.bedrock_session_token:
                self.session_kwargs["aws_session_token"] = (
                    settings.bedrock_session_token
                )

        self.session = aioboto3.Session(**self.session_kwargs)

    async def _invoke_model(
        self, system: str, messages: list[dict[str, str]], max_tokens: int = 2048
    ) -> str:
        """Invoke the Bedrock model with the given system prompt and messages."""
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }

        async with self.session.client(
            "bedrock-runtime", region_name=self.region
        ) as client:
            response = await client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body),
            )

            response_body = await response["body"].read()
            result = json.loads(response_body)
            return result["content"][0]["text"]

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        result = json.loads(json_str)

        # Handle case where LLM returns an array instead of an object
        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        if not isinstance(result, dict):
            raise ValueError(f"Expected dict, got {type(result).__name__}")

        return result

    def _get_default_visualization(
        self, columns: list[str], natural_language: str
    ) -> dict[str, Any]:
        """Get default visualization when LLM fails."""
        x_key = columns[0] if columns else "x"
        y_key = columns[1] if len(columns) > 1 else columns[0] if columns else "y"

        return {
            "chart_type": "bar",
            "title": (
                natural_language[:50] + "..."
                if len(natural_language) > 50
                else natural_language
            ),
            "description": "Data visualization",
            "chart_config": {
                "x_axis": {"data_key": x_key, "label": x_key},
                "y_axis": {"data_key": y_key, "label": y_key},
                "series": [{"data_key": y_key, "name": y_key, "color": "#8884d8"}],
                "legend": True,
                "tooltip": True,
                "grid": True,
            },
            "reasoning": "Default bar chart visualization",
        }

    def _build_visualization_prompt(
        self,
        dashboard_context: dict[str, Any],
        data_samples: list[dict[str, Any]],
        preferences: dict[str, Any] | None = None,
    ) -> str:
        """Build the user prompt for visualization generation."""
        parts = [
            f"Dashboard Title: {dashboard_context.get('title', 'Dashboard')}",
            f"Description: {dashboard_context.get('description', 'No description provided')}",
        ]

        # Add user query if provided
        if dashboard_context.get("user_query"):
            parts.append(f"\nUser Request: {dashboard_context['user_query']}")

        # Add schema information for each data source
        if dashboard_context.get("schemas"):
            parts.append("\n--- Data Source Schemas ---")
            for schema in dashboard_context["schemas"]:
                parts.append(f"\nData Source: {schema.get('name', 'Unknown')}")
                parts.append(
                    f"Schema:\n{json.dumps(schema.get('schema', {}), indent=2)}"
                )

        # Add sample data
        if data_samples:
            parts.append("\n--- Sample Data (first 10 rows per source) ---")
            for sample in data_samples:
                parts.append(f"\nData Source: {sample.get('name', 'Unknown')}")
                rows = sample.get("rows", [])[:10]
                parts.append(f"Columns: {sample.get('columns', [])}")
                parts.append(
                    f"Sample Rows ({len(rows)} of {sample.get('total_rows', 0)}):"
                )
                parts.append(json.dumps(rows, indent=2))

        # Add preferences if provided
        if preferences:
            parts.append("\n--- Visualization Preferences ---")
            if preferences.get("chart_types"):
                parts.append(
                    f"Preferred chart types: {', '.join(preferences['chart_types'])}"
                )
            if preferences.get("color_scheme"):
                parts.append(f"Color scheme: {preferences['color_scheme']}")
            if preferences.get("layout"):
                parts.append(f"Layout: {preferences['layout']}")

        parts.append("\nGenerate React visualization code for this dashboard.")

        return "\n".join(parts)

    def _extract_code_from_response(self, content: str) -> str:
        """Extract code from a response that may contain markdown code blocks."""
        # Try to find React/JavaScript code blocks
        for lang in ["jsx", "tsx", "javascript", "typescript", "react"]:
            marker = f"```{lang}"
            if marker in content:
                return content.split(marker)[1].split("```")[0].strip()

        # Fallback to generic code block
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                return parts[1].strip()

        return content

    async def generate_query(
        self,
        natural_language: str,
        schema_info: dict[str, Any],
        context: str | None = None,
        source_type: str = "postgresql",
    ) -> dict[str, Any]:
        """Generate a query from natural language using Bedrock Claude."""
        system_prompt = """You are a data analyst assistant that converts natural language questions into PostgreSQL queries.
Given a database schema and a natural language question, generate a SQL query that answers the question.

IMPORTANT RULES:
1. Return ONLY valid PostgreSQL SQL that can be executed directly
2. Use double quotes for table and column names that may conflict with reserved words
3. Limit results to a reasonable number (e.g., LIMIT 100) unless aggregating
4. Use appropriate JOINs when data spans multiple tables
5. Handle NULL values appropriately
6. Include ORDER BY for meaningful sorting when applicable

Respond with a JSON object containing:
- "query": The SQL query as a string (no markdown, no code blocks, just the SQL)
- "query_type": Always "sql"
- "explanation": Brief explanation of what the query does"""
        query_type_label = "sql"
        instruction = "Generate the PostgreSQL query to answer this question."

        user_message = f"""Schema Information:
{json.dumps(schema_info, indent=2)}

{f"Additional Context: {context}" if context else ""}

Natural Language Question: {natural_language}

{instruction}"""

        try:
            content = await self._invoke_model(
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=2048,
            )

            # Parse JSON response
            try:
                result = self._parse_json_response(content)
                return {
                    "query": result.get("query", ""),
                    "query_type": result.get("query_type", query_type_label),
                    "explanation": result.get("explanation", ""),
                }
            except (json.JSONDecodeError, ValueError, KeyError, IndexError) as e:
                logger.warning(
                    "Failed to parse JSON response from LLM",
                    error=str(e),
                    content_preview=content[:200] if content else "empty",
                )
                raise LLMResponseError(
                    f"Failed to parse query response from LLM: {str(e)}"
                )

        except LLMResponseError:
            raise
        except Exception as e:
            logger.error("Error generating query", error=str(e))
            raise LLMConnectionError(f"Failed to generate query: {str(e)}")

    async def recommend_visualization(
        self,
        query_result: dict[str, Any],
        natural_language: str,
    ) -> dict[str, Any]:
        """Recommend a visualization for query results using Bedrock Claude."""
        system_prompt = """You are a data visualization expert that recommends the best chart type for given data.
Analyze the data and the user's original question to recommend an appropriate visualization.

Available chart types: line, bar, pie, area, scatter, composed

RULES:
1. Consider the data structure (time series, categorical, numerical relationships)
2. Consider what insight the user is trying to gain
3. Provide Recharts-compatible configuration
4. Keep the configuration simple but complete

Respond with a JSON object containing:
- "chart_type": One of [line, bar, pie, area, scatter, composed]
- "title": A descriptive title for the visualization
- "description": Brief description of what the chart shows
- "chart_config": Object with Recharts configuration:
  - "x_axis": {"data_key": "column_name", "label": "X Axis Label"}
  - "y_axis": {"data_key": "column_name", "label": "Y Axis Label"} (optional for pie)
  - "series": [{"data_key": "column_name", "name": "Display Name", "color": "#hex"}]
  - "legend": true/false
  - "tooltip": true/false
  - "grid": true/false
- "reasoning": Why this visualization was chosen"""

        # Prepare data sample for analysis
        columns = query_result.get("columns", [])
        rows = query_result.get("rows", [])[:10]  # Limit to 10 rows for analysis

        user_message = f"""Original Question: {natural_language}

Data Columns: {columns}

Sample Data (first 10 rows):
{json.dumps(rows, indent=2)}

Total Rows: {query_result.get("row_count", len(rows))}

Recommend the best visualization for this data."""

        try:
            content = await self._invoke_model(
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=2048,
            )

            # Parse JSON response
            try:
                result = self._parse_json_response(content)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse visualization JSON, using defaults")
                return self._get_default_visualization(columns, natural_language)

        except Exception as e:
            logger.error("Error recommending visualization", error=str(e))
            raise LLMResponseError(f"Failed to recommend visualization: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Bedrock API is available."""
        try:
            # Simple API check - just verify we can invoke the model
            await self._invoke_model(
                system="You are a helpful assistant.",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.error("Bedrock health check failed", error=str(e))
            return False

    async def generate_react_visualization(
        self,
        dashboard_context: dict[str, Any],
        data_samples: list[dict[str, Any]],
        preferences: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate React visualization code for a dashboard using Bedrock Claude."""
        system_prompt = """You are an expert React developer specializing in data visualization.
Generate production-ready React code using:
- React 18+ functional components with hooks
- Recharts library for all visualizations
- Tailwind CSS for styling
- Responsive design with ResponsiveContainer

IMPORTANT RULES:
1. Create a single exportable Dashboard component
2. Use ResponsiveContainer for all charts to ensure responsiveness
3. Include proper TypeScript-style prop types in comments
4. Use Tailwind CSS classes for all styling
5. Make the code self-contained and immediately usable
6. Include sample data transformation if needed
7. Use modern React patterns (hooks, functional components)

Respond with a JSON object containing:
- "react_code": Complete exportable Dashboard component code as a string
- "components": Array of objects with: name, chart_type, description, data_keys
- "reasoning": Brief explanation of design decisions"""

        # Build user message with dashboard context
        user_message = self._build_visualization_prompt(
            dashboard_context, data_samples, preferences
        )

        try:
            content = await self._invoke_model(
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=8192,
            )

            # Parse JSON response
            try:
                result = self._parse_json_response(content)

                # Ensure components have required fields with proper defaults
                components = result.get("components", [])
                if isinstance(components, list):
                    for comp in components:
                        if isinstance(comp, dict) and comp.get("data_keys") is None:
                            comp["data_keys"] = []

                return {
                    "react_code": result.get("react_code", ""),
                    "components": components,
                    "reasoning": result.get("reasoning", ""),
                    "model": self.model_id,
                }
            except json.JSONDecodeError:
                logger.warning("Failed to parse visualization JSON, extracting code")
                # Try to extract code block directly
                code = self._extract_code_from_response(content)
                return {
                    "react_code": code,
                    "components": [],
                    "reasoning": "Generated React visualization code",
                    "model": self.model_id,
                }

        except Exception as e:
            logger.error("Error generating React visualization", error=str(e))
            raise LLMResponseError(f"Failed to generate visualization: {str(e)}")
