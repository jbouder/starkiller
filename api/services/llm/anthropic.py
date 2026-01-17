"""Anthropic Claude LLM provider implementation."""

import json
from typing import Any

from anthropic import AsyncAnthropic

from config import get_settings
from core.exceptions import LLMConnectionError, LLMResponseError
from core.logging import get_logger
from services.llm.base import BaseLLMProvider

logger = get_logger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude implementation for LLM operations."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    async def generate_query(
        self,
        natural_language: str,
        schema_info: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Generate a pandas query from natural language using Claude."""
        system_prompt = """You are a data analyst assistant that converts natural language questions into pandas code.
Given a data schema and a natural language question, generate Python pandas code that answers the question.

IMPORTANT RULES:
1. Always assume the DataFrame is named 'df'
2. Return ONLY valid Python code that can be executed
3. The code should result in a DataFrame or Series that answers the question
4. Use standard pandas operations (groupby, filter, sort, aggregate, etc.)
5. Handle missing values appropriately
6. Include comments explaining key steps

Respond with a JSON object containing:
- "query": The pandas code as a string
- "query_type": Always "pandas"
- "explanation": Brief explanation of what the code does"""

        user_message = f"""Schema Information:
{json.dumps(schema_info, indent=2)}

{f'Additional Context: {context}' if context else ''}

Natural Language Question: {natural_language}

Generate the pandas code to answer this question."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text

            # Parse JSON response
            try:
                # Try to extract JSON from the response
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()

                result = json.loads(json_str)
                return {
                    "query": result.get("query", ""),
                    "query_type": result.get("query_type", "pandas"),
                    "explanation": result.get("explanation", ""),
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract code directly
                logger.warning("Failed to parse JSON response, extracting code directly")
                return {
                    "query": content,
                    "query_type": "pandas",
                    "explanation": "Generated pandas code",
                }

        except Exception as e:
            logger.error("Error generating query", error=str(e))
            raise LLMConnectionError(f"Failed to generate query: {str(e)}")

    async def recommend_visualization(
        self,
        query_result: dict[str, Any],
        natural_language: str,
    ) -> dict[str, Any]:
        """Recommend a visualization for query results using Claude."""
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

Total Rows: {query_result.get('row_count', len(rows))}

Recommend the best visualization for this data."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text

            # Parse JSON response
            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()

                result = json.loads(json_str)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse visualization JSON, using defaults")
                # Return a sensible default
                return self._get_default_visualization(columns, natural_language)

        except Exception as e:
            logger.error("Error recommending visualization", error=str(e))
            raise LLMResponseError(f"Failed to recommend visualization: {str(e)}")

    def _get_default_visualization(
        self, columns: list[str], natural_language: str
    ) -> dict[str, Any]:
        """Get default visualization when LLM fails."""
        x_key = columns[0] if columns else "x"
        y_key = columns[1] if len(columns) > 1 else columns[0] if columns else "y"

        return {
            "chart_type": "bar",
            "title": natural_language[:50] + "..." if len(natural_language) > 50 else natural_language,
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

    async def health_check(self) -> bool:
        """Check if Anthropic API is available."""
        try:
            # Simple API check - just verify we can create a short message
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return bool(response.content)
        except Exception as e:
            logger.error("Anthropic health check failed", error=str(e))
            return False
