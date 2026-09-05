"""Tests for GET /api/v1/health endpoint."""

from datetime import datetime


def test_health_check_endpoint(admin_client):
    """Test GET /api/v1/health returns 200 OK and expected HealthCheckResponse structure."""
    response = admin_client.get("/api/v1/health")

    # Assert Status Code & Content Type
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    # Validate Schema Fields
    assert "status" in data
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data

    # Validate Value Constraints
    assert data["status"] == "healthy"
    assert data["service"] == "SIH 26189 Criminal Network Analysis System"
    assert data["version"] == "0.1.0"

    # Validate Timestamp ISO-8601 Formatting
    parsed_dt = datetime.fromisoformat(data["timestamp"])
    assert parsed_dt is not None


def test_root_info_endpoint(admin_client):
    """Test GET / returns 200 OK service metadata."""
    response = admin_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["synthetic_data_policy"] == "Strictly Synthetic Data Only"
