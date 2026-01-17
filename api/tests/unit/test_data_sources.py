"""Unit tests for data source endpoints."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


class TestDataSourceEndpoints:
    """Tests for data source CRUD endpoints."""

    def test_create_data_source(
        self, client: TestClient, sample_data_source_config: dict[str, Any]
    ):
        """Test creating a data source."""
        response = client.post("/api/v1/data-sources", json=sample_data_source_config)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_data_source_config["name"]
        assert data["source_type"] == sample_data_source_config["source_type"]
        assert "id" in data
        assert data["is_active"] is True

    def test_list_data_sources(
        self, client: TestClient, sample_data_source_config: dict[str, Any]
    ):
        """Test listing data sources."""
        # Create a data source first
        client.post("/api/v1/data-sources", json=sample_data_source_config)

        response = client.get("/api/v1/data-sources")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_data_source(
        self, client: TestClient, sample_data_source_config: dict[str, Any]
    ):
        """Test getting a specific data source."""
        # Create a data source first
        create_response = client.post(
            "/api/v1/data-sources", json=sample_data_source_config
        )
        data_source_id = create_response.json()["id"]

        response = client.get(f"/api/v1/data-sources/{data_source_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == data_source_id
        assert data["name"] == sample_data_source_config["name"]

    def test_get_nonexistent_data_source(self, client: TestClient):
        """Test getting a data source that doesn't exist."""
        response = client.get("/api/v1/data-sources/nonexistent-id")
        assert response.status_code == 404

    def test_update_data_source(
        self, client: TestClient, sample_data_source_config: dict[str, Any]
    ):
        """Test updating a data source."""
        # Create a data source first
        create_response = client.post(
            "/api/v1/data-sources", json=sample_data_source_config
        )
        data_source_id = create_response.json()["id"]

        update_data = {"name": "Updated Name", "is_active": False}
        response = client.patch(
            f"/api/v1/data-sources/{data_source_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_active"] is False

    def test_delete_data_source(
        self, client: TestClient, sample_data_source_config: dict[str, Any]
    ):
        """Test deleting a data source."""
        # Create a data source first
        create_response = client.post(
            "/api/v1/data-sources", json=sample_data_source_config
        )
        data_source_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/data-sources/{data_source_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/data-sources/{data_source_id}")
        assert get_response.status_code == 404
