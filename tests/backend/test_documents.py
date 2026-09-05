"""Tests for Document endpoints: POST and GET under /api/v1/cases/{case_id}/documents."""


class TestCreateDocument:
    """Tests for POST /api/v1/cases/{case_id}/documents."""

    def _create_case(self, admin_client) -> str:
        """Helper — create a case and return its ID."""
        resp = admin_client.post("/api/v1/cases", json={
            "case_number": "CASE-DOC-001",
            "title": "Document Test Case",
        })
        return resp.json()["id"]

    def test_create_document_success(self, admin_client):
        """Upload a document to an existing case."""
        case_id = self._create_case(admin_client)

        payload = {
            "file_name": "synthetic_cdr_batch_001.csv",
            "file_type": "CDR",
            "raw_content": "caller,callee,duration,timestamp\n+1-555-0001,+1-555-0002,120,2026-08-15T14:30:00Z",
        }
        response = admin_client.post(f"/api/v1/cases/{case_id}/documents", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["file_name"] == "synthetic_cdr_batch_001.csv"
        assert data["file_type"] == "CDR"
        assert data["status"] == "UPLOADED"
        assert data["case_id"] == case_id
        assert data["file_hash"] is not None  # SHA-256 generated from content

    def test_create_document_case_not_found(self, admin_client):
        """Upload to non-existent case returns 404."""
        payload = {
            "file_name": "orphan.csv",
            "file_type": "CDR",
        }
        response = admin_client.post("/api/v1/cases/non-existent-uuid/documents", json=payload)
        assert response.status_code == 404

    def test_create_document_invalid_type(self, admin_client):
        """Invalid file_type returns 422."""
        case_id = self._create_case(admin_client)
        payload = {
            "file_name": "bad_type.csv",
            "file_type": "INVALID_TYPE",
        }
        response = admin_client.post(f"/api/v1/cases/{case_id}/documents", json=payload)
        assert response.status_code == 422


class TestListDocuments:
    """Tests for GET /api/v1/cases/{case_id}/documents."""

    def test_list_documents_empty(self, admin_client):
        """Case with no documents returns empty list."""
        resp = admin_client.post("/api/v1/cases", json={
            "case_number": "CASE-DOCLIST-001",
            "title": "Empty Docs Case",
        })
        case_id = resp.json()["id"]

        response = admin_client.get(f"/api/v1/cases/{case_id}/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["documents"] == []

    def test_list_documents_returns_uploaded(self, admin_client):
        """Uploaded documents appear in the list."""
        resp = admin_client.post("/api/v1/cases", json={
            "case_number": "CASE-DOCLIST-002",
            "title": "Populated Docs Case",
        })
        case_id = resp.json()["id"]

        admin_client.post(f"/api/v1/cases/{case_id}/documents", json={
            "file_name": "report_alpha.txt",
            "file_type": "TEXT_REPORT",
            "raw_content": "Subject A was observed meeting Subject B at Location X.",
        })

        response = admin_client.get(f"/api/v1/cases/{case_id}/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["documents"][0]["file_name"] == "report_alpha.txt"

    def test_list_documents_case_not_found(self, admin_client):
        """Listing documents for non-existent case returns 404."""
        response = admin_client.get("/api/v1/cases/non-existent-uuid/documents")
        assert response.status_code == 404


class TestDocumentAuditLogging:
    """Tests that document operations create audit log entries."""

    def test_upload_document_generates_audit_log(self, admin_client, db_session):
        """Uploading a document produces an audit log entry."""
        from apps.backend.app.models.audit_log import AuditLog

        resp = admin_client.post("/api/v1/cases", json={
            "case_number": "CASE-DOCAUDIT-001",
            "title": "Doc Audit Case",
        })
        case_id = resp.json()["id"]

        admin_client.post(f"/api/v1/cases/{case_id}/documents", json={
            "file_name": "audit_test.csv",
            "file_type": "BANK_STATEMENT",
        })

        logs = db_session.query(AuditLog).filter(
            AuditLog.action == "UPLOAD_DOCUMENT"
        ).all()
        assert len(logs) >= 1
        assert logs[0].target_type == "DOCUMENT"
