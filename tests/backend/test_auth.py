"""Tests for authentication and RBAC."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case import Case
from apps.backend.app.schemas.case import CaseStatus
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel


def test_unauthenticated_access_denied(unauthenticated_client: TestClient):
    """Test that public endpoints are open, but protected endpoints return 401."""
    # Public
    response = unauthenticated_client.get("/api/v1/health")
    assert response.status_code == 200

    # Protected
    response = unauthenticated_client.get("/api/v1/cases")
    assert response.status_code == 401


def test_login_success(unauthenticated_client: TestClient, test_users: dict[str, User]):
    """Test that login works with valid credentials."""
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        data={"username": "test_investigator", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == Role.INVESTIGATOR.value


def test_login_failure(unauthenticated_client: TestClient, test_users: dict[str, User]):
    """Test that login fails with invalid credentials."""
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        data={"username": "test_investigator", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_investigator_creates_case_and_gets_access(
    investigator_client: TestClient, db_session: Session
):
    """Test that an investigator can create a case and is automatically assigned MANAGE access."""
    # Create case
    case_data = {
        "case_number": "TEST-100",
        "title": "Test Case",
        "description": "A test case",
        "status": CaseStatus.ACTIVE.value,
        "priority": "HIGH"
    }
    response = investigator_client.post("/api/v1/cases", json=case_data)
    assert response.status_code == 201, response.text
    case_id = response.json()["id"]

    # Verify case access
    access = db_session.query(CaseAccess).filter(CaseAccess.case_id == case_id).first()
    assert access is not None
    assert access.access_level == CaseAccessLevel.MANAGE.value
    assert access.is_active is True


def test_reviewer_denied_case_creation(reviewer_client: TestClient):
    """Test that reviewers cannot create cases."""
    case_data = {
        "case_number": "TEST-200",
        "title": "Test Case",
    }
    response = reviewer_client.post("/api/v1/cases", json=case_data)
    assert response.status_code == 403


def test_case_access_isolation(
    admin_client: TestClient,
    investigator_client: TestClient,
    analyst_client: TestClient,
    test_users: dict[str, User],
    db_session: Session
):
    """Test that users can only see cases they are assigned to, but admins can see all."""
    # Investigator creates case A
    res_a = investigator_client.post("/api/v1/cases", json={"case_number": "C-A", "title": "A", "status": "ACTIVE", "priority": "HIGH"})
    case_a_id = res_a.json()["id"]

    # Analyst gets 403 on Case A
    assert analyst_client.get(f"/api/v1/cases/{case_a_id}").status_code == 403

    # Admin can see Case A
    assert admin_client.get(f"/api/v1/cases/{case_a_id}").status_code == 200

    # Assign analyst to Case A with VIEW access
    access = CaseAccess(
        user_id=test_users[Role.ANALYST.value].id,
        case_id=case_a_id,
        access_level=CaseAccessLevel.VIEW.value,
        is_active=True
    )
    db_session.add(access)
    db_session.commit()

    # Analyst can now VIEW Case A
    assert analyst_client.get(f"/api/v1/cases/{case_a_id}").status_code == 200

    # But Analyst cannot UPDATE Case A (requires MANAGE)
    assert analyst_client.patch(f"/api/v1/cases/{case_a_id}", json={"title": "Updated"}).status_code == 403

    # Investigator can UPDATE Case A
    assert investigator_client.patch(f"/api/v1/cases/{case_a_id}", json={"title": "Updated"}).status_code == 200
