"""Unit tests for AWS Bedrock LLM provider."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.llm.bedrock import BedrockProvider


@pytest.fixture
def mock_settings():
    """Create mock settings for Bedrock provider."""
    settings = MagicMock()
    settings.bedrock_model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    settings.bedrock_region = "us-east-1"
    settings.bedrock_access_key_id = ""
    settings.bedrock_secret_access_key = ""
    settings.bedrock_session_token = ""
    return settings


@pytest.fixture
def mock_settings_with_credentials():
    """Create mock settings with explicit credentials."""
    settings = MagicMock()
    settings.bedrock_model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    settings.bedrock_region = "us-east-1"
    settings.bedrock_access_key_id = "AKIAIOSFODNN7EXAMPLE"
    settings.bedrock_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    settings.bedrock_session_token = "session-token-example"
    return settings


class TestBedrockProvider:
    """Tests for Bedrock LLM provider."""

    @patch("services.llm.bedrock.get_settings")
    def test_init_without_credentials(self, mock_get_settings, mock_settings):
        """Test initialization without explicit credentials uses credential chain."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        assert provider.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert provider.region == "us-east-1"
        assert provider.session_kwargs == {}

    @patch("services.llm.bedrock.get_settings")
    def test_init_with_credentials(
        self, mock_get_settings, mock_settings_with_credentials
    ):
        """Test initialization with explicit credentials."""
        mock_get_settings.return_value = mock_settings_with_credentials

        provider = BedrockProvider()

        assert provider.session_kwargs["aws_access_key_id"] == "AKIAIOSFODNN7EXAMPLE"
        assert (
            provider.session_kwargs["aws_secret_access_key"]
            == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
        assert provider.session_kwargs["aws_session_token"] == "session-token-example"

    @patch("services.llm.bedrock.get_settings")
    async def test_generate_query_success(self, mock_get_settings, mock_settings):
        """Test successful query generation."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        # Mock the response
        mock_response = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "query": "SELECT * FROM users LIMIT 100",
                            "query_type": "sql",
                            "explanation": "Fetches all users with a limit of 100",
                        }
                    )
                }
            ]
        }

        # Create a mock body that supports async read
        mock_body = AsyncMock()
        mock_body.read.return_value = json.dumps(mock_response).encode()

        # Mock the bedrock client
        mock_client = AsyncMock()
        mock_client.invoke_model.return_value = {"body": mock_body}

        # Mock the session context manager
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_client
        mock_context_manager.__aexit__.return_value = None

        provider.session = MagicMock()
        provider.session.client.return_value = mock_context_manager

        result = await provider.generate_query(
            natural_language="Get all users",
            schema_info={"tables": [{"name": "users", "columns": ["id", "name"]}]},
        )

        assert result["query"] == "SELECT * FROM users LIMIT 100"
        assert result["query_type"] == "sql"
        assert "Fetches all users" in result["explanation"]

    @patch("services.llm.bedrock.get_settings")
    async def test_health_check_success(self, mock_get_settings, mock_settings):
        """Test successful health check."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        # Mock successful response
        mock_response = {"content": [{"text": "Hello!"}]}

        mock_body = AsyncMock()
        mock_body.read.return_value = json.dumps(mock_response).encode()

        mock_client = AsyncMock()
        mock_client.invoke_model.return_value = {"body": mock_body}

        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_client
        mock_context_manager.__aexit__.return_value = None

        provider.session = MagicMock()
        provider.session.client.return_value = mock_context_manager

        result = await provider.health_check()

        assert result is True

    @patch("services.llm.bedrock.get_settings")
    async def test_health_check_failure(self, mock_get_settings, mock_settings):
        """Test health check returns False on error."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        # Mock the client to raise an exception
        mock_client = AsyncMock()
        mock_client.invoke_model.side_effect = Exception("Connection failed")

        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_client
        mock_context_manager.__aexit__.return_value = None

        provider.session = MagicMock()
        provider.session.client.return_value = mock_context_manager

        result = await provider.health_check()

        assert result is False

    @patch("services.llm.bedrock.get_settings")
    async def test_recommend_visualization_success(
        self, mock_get_settings, mock_settings
    ):
        """Test successful visualization recommendation."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        mock_response = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "chart_type": "bar",
                            "title": "Sales by Month",
                            "description": "Monthly sales data",
                            "chart_config": {
                                "x_axis": {"data_key": "month", "label": "Month"},
                                "y_axis": {"data_key": "sales", "label": "Sales"},
                                "series": [
                                    {
                                        "data_key": "sales",
                                        "name": "Sales",
                                        "color": "#8884d8",
                                    }
                                ],
                                "legend": True,
                                "tooltip": True,
                                "grid": True,
                            },
                            "reasoning": "Bar chart is best for comparing categories",
                        }
                    )
                }
            ]
        }

        mock_body = AsyncMock()
        mock_body.read.return_value = json.dumps(mock_response).encode()

        mock_client = AsyncMock()
        mock_client.invoke_model.return_value = {"body": mock_body}

        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_client
        mock_context_manager.__aexit__.return_value = None

        provider.session = MagicMock()
        provider.session.client.return_value = mock_context_manager

        result = await provider.recommend_visualization(
            query_result={
                "columns": ["month", "sales"],
                "rows": [
                    {"month": "Jan", "sales": 100},
                    {"month": "Feb", "sales": 150},
                ],
                "row_count": 2,
            },
            natural_language="Show me monthly sales",
        )

        assert result["chart_type"] == "bar"
        assert result["title"] == "Sales by Month"

    @patch("services.llm.bedrock.get_settings")
    async def test_generate_react_visualization_success(
        self, mock_get_settings, mock_settings
    ):
        """Test successful React visualization generation."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        mock_response = {
            "content": [
                {
                    "text": json.dumps(
                        {
                            "react_code": "const Dashboard = () => { return <div>Chart</div> }",
                            "components": [
                                {
                                    "name": "SalesChart",
                                    "chart_type": "bar",
                                    "description": "Sales bar chart",
                                    "data_keys": ["month", "sales"],
                                }
                            ],
                            "reasoning": "Simple bar chart for sales data",
                        }
                    )
                }
            ]
        }

        mock_body = AsyncMock()
        mock_body.read.return_value = json.dumps(mock_response).encode()

        mock_client = AsyncMock()
        mock_client.invoke_model.return_value = {"body": mock_body}

        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_client
        mock_context_manager.__aexit__.return_value = None

        provider.session = MagicMock()
        provider.session.client.return_value = mock_context_manager

        result = await provider.generate_react_visualization(
            dashboard_context={"title": "Sales Dashboard", "description": "Dashboard"},
            data_samples=[
                {
                    "name": "Sales",
                    "columns": ["month", "sales"],
                    "rows": [{"month": "Jan", "sales": 100}],
                    "total_rows": 1,
                }
            ],
        )

        assert "Dashboard" in result["react_code"]
        assert result["model"] == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert len(result["components"]) == 1

    @patch("services.llm.bedrock.get_settings")
    def test_credentials_optional(self, mock_get_settings, mock_settings):
        """Test that provider works without explicit credentials."""
        mock_get_settings.return_value = mock_settings

        # Should not raise an error
        provider = BedrockProvider()

        # Verify no credentials in session kwargs
        assert "aws_access_key_id" not in provider.session_kwargs
        assert "aws_secret_access_key" not in provider.session_kwargs
        assert "aws_session_token" not in provider.session_kwargs

    @patch("services.llm.bedrock.get_settings")
    def test_parse_json_response_with_markdown(self, mock_get_settings, mock_settings):
        """Test parsing JSON response wrapped in markdown code blocks."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        content = '```json\n{"key": "value"}\n```'
        result = provider._parse_json_response(content)

        assert result == {"key": "value"}

    @patch("services.llm.bedrock.get_settings")
    def test_parse_json_response_plain(self, mock_get_settings, mock_settings):
        """Test parsing plain JSON response."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        content = '{"key": "value"}'
        result = provider._parse_json_response(content)

        assert result == {"key": "value"}

    @patch("services.llm.bedrock.get_settings")
    def test_get_default_visualization(self, mock_get_settings, mock_settings):
        """Test default visualization fallback."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        result = provider._get_default_visualization(
            columns=["x_col", "y_col"], natural_language="Test query"
        )

        assert result["chart_type"] == "bar"
        assert result["chart_config"]["x_axis"]["data_key"] == "x_col"
        assert result["chart_config"]["y_axis"]["data_key"] == "y_col"

    @patch("services.llm.bedrock.get_settings")
    def test_extract_code_from_response_jsx(self, mock_get_settings, mock_settings):
        """Test extracting JSX code from markdown response."""
        mock_get_settings.return_value = mock_settings

        provider = BedrockProvider()

        content = '```jsx\nconst App = () => <div>Hello</div>\n```'
        result = provider._extract_code_from_response(content)

        assert result == "const App = () => <div>Hello</div>"
