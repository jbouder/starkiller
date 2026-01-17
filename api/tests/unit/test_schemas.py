"""Unit tests for Pydantic schemas."""

import pytest

from schemas.data_source import ConnectionConfig, DataSourceCreate
from schemas.query import QueryRequest
from schemas.visualization import ChartConfig, AxisConfig, SeriesConfig


class TestDataSourceSchemas:
    """Tests for data source schemas."""

    def test_connection_config_csv(self):
        """Test CSV connection config."""
        config = ConnectionConfig(file_path="/path/to/file.csv")
        assert config.file_path == "/path/to/file.csv"
        assert config.host is None

    def test_connection_config_postgresql(self):
        """Test PostgreSQL connection config."""
        config = ConnectionConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
        )
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "testdb"

    def test_data_source_create(self):
        """Test data source create schema."""
        data = DataSourceCreate(
            name="Test Source",
            description="A test source",
            source_type="csv",
            connection_config=ConnectionConfig(file_path="/path/to/file.csv"),
        )
        assert data.name == "Test Source"
        assert data.source_type == "csv"


class TestQuerySchemas:
    """Tests for query schemas."""

    def test_query_request(self):
        """Test query request schema."""
        request = QueryRequest(
            query="Show me sales by region",
            data_source_id="123",
        )
        assert request.query == "Show me sales by region"
        assert request.data_source_id == "123"

    def test_query_request_without_data_source(self):
        """Test query request without data source."""
        request = QueryRequest(query="Show me all data")
        assert request.query == "Show me all data"
        assert request.data_source_id is None


class TestVisualizationSchemas:
    """Tests for visualization schemas."""

    def test_axis_config(self):
        """Test axis configuration."""
        axis = AxisConfig(data_key="month", label="Month", type="category")
        assert axis.data_key == "month"
        assert axis.label == "Month"
        assert axis.type == "category"

    def test_series_config(self):
        """Test series configuration."""
        series = SeriesConfig(
            data_key="sales",
            name="Total Sales",
            color="#8884d8",
        )
        assert series.data_key == "sales"
        assert series.name == "Total Sales"
        assert series.color == "#8884d8"

    def test_chart_config(self):
        """Test chart configuration."""
        config = ChartConfig(
            x_axis=AxisConfig(data_key="month", label="Month"),
            y_axis=AxisConfig(data_key="sales", label="Sales"),
            series=[SeriesConfig(data_key="sales", name="Sales")],
            legend=True,
            tooltip=True,
            grid=True,
        )
        assert config.x_axis.data_key == "month"
        assert len(config.series) == 1
        assert config.legend is True
