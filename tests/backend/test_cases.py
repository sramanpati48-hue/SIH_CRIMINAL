"""Tests for Case CRUD endpoints: POST, GET, GET/{id}, PATCH/{id}."""

from datetime import datetime


class TestCreateCase:
    """Tests for POST /api/v1/cases."""

    def test_create_case_success(self, client):
        """Create a case with valid data."""
        payload = {
            "case_number": "CASE-SYNTH-001",
            "title": "Operation Synthetic Network Alpha",
            "description": "Synthetic investigation into mock financial network.",
            "priority": "HIGH",
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["case_number"] == "CASE-SYNTH-001"
        assert data["title"] == "Operation Synthetic Network Alpha"
        assert data["status"] == "ACTIVE"
        assert data["priority"] == "HIGH"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Validate timestamp format
        datetime.fromisoformat(data["created_at"])

    def test_create_case_default_priority(self, client):
        """Case should default to MEDIUM priority."""
        payload = {
            "case_number": "CASE-SYNTH-002",
            "title": "Default Priority Test",
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 201
        assert response.json()["priority"] == "MEDIUM"

    def test_create_case_duplicate_number_rejected(self, client):
        """Duplicate case number returns 409 Conflict."""
        payload = {
            "case_number": "CASE-DUP-001",
            "title": "First Case",
        }
        response1 = client.post("/api/v1/cases", json=payload)
        assert response1.status_code == 201

        payload2 = {
            "case_number": "CASE-DUP-001",
            "title": "Duplicate Case",
        }
        response2 = client.post("/api/v1/cases", json=payload2)
        assert response2.status_code == 409

    def test_create_case_missing_required_fields(self, client):
        """Missing required fields returns 422 Validation Error."""
        response = client.post("/api/v1/cases", json={})
        assert response.status_code == 422


class TestListCases:
    """Tests for GET /api/v1/cases."""

    def test_list_cases_empty(self, client):
        """Empty database returns zero cases."""
        response = client.get("/api/v1/cases")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["cases"] == []

    def test_list_cases_returns_created(self, client):
        """Created cases appear in the list."""
        client.post("/api/v1/cases", json={
            "case_number": "CASE-LIST-001",
            "title": "List Test Case",
        })
        response = client.get("/api/v1/cases")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["cases"][0]["case_number"] == "CASE-LIST-001"

    def test_list_cases_status_filter(self, client):
        """Status filter returns only matching cases."""
        client.post("/api/v1/cases", json={
            "case_number": "CASE-FILTER-001",
            "title": "Active Case",
        })
        response = client.get("/api/v1/cases?status=CLOSED")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestGetCase:
    """Tests for GET /api/v1/cases/{case_id}."""

    def test_get_case_success(self, client):
        """Retrieve an existing case by ID."""
        create_resp = client.post("/api/v1/cases", json={
            "case_number": "CASE-GET-001",
            "title": "Get Test Case",
        })
        case_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/cases/{case_id}")
        assert response.status_code == 200
        assert response.json()["case_number"] == "CASE-GET-001"

    def test_get_case_not_found(self, client):
        """Non-existent case ID returns 404."""
        response = client.get("/api/v1/cases/non-existent-uuid")
        assert response.status_code == 404


class TestUpdateCase:
    """Tests for PATCH /api/v1/cases/{case_id}."""

    def test_update_case_title(self, client):
        """Partial update of case title."""
        create_resp = client.post("/api/v1/cases", json={
            "case_number": "CASE-UPD-001",
            "title": "Original Title",
        })
        case_id = create_resp.json()["id"]

        response = client.patch(f"/api/v1/cases/{case_id}", json={
            "title": "Updated Title",
        })
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
        assert response.json()["case_number"] == "CASE-UPD-001"

    def test_update_case_status(self, client):
        """Change case status to CLOSED."""
        create_resp = client.post("/api/v1/cases", json={
            "case_number": "CASE-UPD-002",
            "title": "Close Me",
        })
        case_id = create_resp.json()["id"]

        response = client.patch(f"/api/v1/cases/{case_id}", json={
            "status": "CLOSED",
        })
        assert response.status_code == 200
        assert response.json()["status"] == "CLOSED"

    def test_update_case_not_found(self, client):
        """Update non-existent case returns 404."""
        response = client.patch("/api/v1/cases/non-existent-uuid", json={
            "title": "No such case",
        })
        assert response.status_code == 404


class TestAuditLogging:
    """Tests that case operations create audit log entries."""

    def test_create_case_generates_audit_log(self, client, db_session):
        """Creating a case produces an audit log entry."""
        from apps.backend.app.models.audit_log import AuditLog

        client.post("/api/v1/cases", json={
            "case_number": "CASE-AUDIT-001",
            "title": "Audit Test Case",
        })

        logs = db_session.query(AuditLog).filter(
            AuditLog.action == "CREATE_CASE"
        ).all()
        assert len(logs) >= 1
        assert logs[0].target_type == "CASE"

    def test_update_case_generates_audit_log(self, client, db_session):
        """Updating a case produces an audit log entry."""
        from apps.backend.app.models.audit_log import AuditLog

        create_resp = client.post("/api/v1/cases", json={
            "case_number": "CASE-AUDIT-002",
            "title": "Audit Update Test",
        })
        case_id = create_resp.json()["id"]

        client.patch(f"/api/v1/cases/{case_id}", json={
            "title": "Audit Updated Title",
        })

        logs = db_session.query(AuditLog).filter(
            AuditLog.action == "UPDATE_CASE",
            AuditLog.target_id == case_id,
        ).all()
        assert len(logs) == 1
        assert '"title"' in (logs[0].previous_state or "")
