"""Tests for Analytics API."""

import pytest
from fastapi.testclient import TestClient

from apps.backend.app.main import app
from apps.backend.app.models.alert import Alert
from apps.backend.app.models.analytics import EntityGraphFeature
from apps.backend.app.analytics.config import analytics_settings

admin_client = TestClient(app)

@pytest.fixture
def mock_case(db_session):
    from apps.backend.app.models.case import Case
    c = Case(id="case-123", case_number="CASE-001", title="Test Case", description="Desc", status="OPEN")
    db_session.add(c)
    db_session.commit()
    return c

@pytest.fixture
def mock_alert(db_session, mock_case):
    a = Alert(
        id="alert-123",
        case_id=mock_case.id,
        alert_type="TEST_PATTERN",
        title="Test Alert",
        description="Desc",
        severity="MEDIUM",
        status="OPEN"
    )
    db_session.add(a)
    db_session.commit()
    return a

def test_analytics_health_offline():
    response = admin_client.get("/api/v1/analytics/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "GRAPH_UNAVAILABLE"]
    assert "gds_available" in data

def test_get_case_patterns_empty(mock_case):
    response = admin_client.get(f"/api/v1/cases/{mock_case.id}/patterns")
    assert response.status_code == 200
    assert response.json() == []

def test_review_alert(mock_alert, db_session):
    response = admin_client.post(
        f"/api/v1/alerts/{mock_alert.id}/review",
        params={"action": "ACCEPT"}
    )
    assert response.status_code == 200
    assert response.json()["new_status"] == "ACCEPTED"
    
    # Check DB
    db_session.refresh(mock_alert)
    assert mock_alert.status == "ACCEPTED"
    
def test_review_alert_requires_rationale(mock_alert):
    response = admin_client.post(
        f"/api/v1/alerts/{mock_alert.id}/review",
        params={"action": "CORRECT"} # Missing rationale
    )
    assert response.status_code == 400
