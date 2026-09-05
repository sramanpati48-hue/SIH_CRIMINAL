"""Tests for audit immutability."""

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.services.audit import log_action

def test_audit_log_has_no_update_delete_methods():
    """Verify that there is no repository layer allowing audit updates."""
    # Since we use direct SQLAlchemy in the service, we ensure no such methods are imported.
    # The service only exposes log_action.
    import apps.backend.app.services.audit as audit_module
    
    assert hasattr(audit_module, "log_action")
    assert not hasattr(audit_module, "update_action")
    assert not hasattr(audit_module, "delete_action")


def test_audit_api_has_no_mutation_routes(admin_client: TestClient):
    """Verify that there are no PUT, PATCH, DELETE routes for audit logs."""
    # Assuming there's a GET route for audit logs if any (maybe in future).
    # We definitely shouldn't be able to mutate them.
    
    res_put = admin_client.put("/api/v1/audit/123", json={"action": "MUTATED"})
    assert res_put.status_code == 404
    
    res_patch = admin_client.patch("/api/v1/audit/123", json={"action": "MUTATED"})
    assert res_patch.status_code == 404
    
    res_delete = admin_client.delete("/api/v1/audit/123")
    assert res_delete.status_code == 404


def test_audit_redacts_passwords_and_tokens(db_session: Session):
    """Test that passwords and tokens are redacted from audit logs."""
    state = {
        "user_id": "123",
        "password": "secretPassword!",
        "password_hash": "$2b$12$...",
        "access_token": "eyJhb...",
        "jwt": "eyJhb...",
        "raw_text": "Sensitive evidence block",
        "document_text": "Long sensitive string",
        "connection_string": "postgresql://user:pass@localhost/db",
        "public_field": "safe_value"
    }
    
    entry = log_action(
        db=db_session,
        action="TEST_ACTION",
        target_type="TEST",
        target_id="test1",
        new_state=state
    )
    
    # Reload and check
    import json
    new_state = json.loads(entry.new_state)
    
    assert new_state["public_field"] == "safe_value"
    assert new_state["user_id"] == "123"
    
    assert new_state["password"] == "[REDACTED]"
    assert new_state["password_hash"] == "[REDACTED]"
    assert new_state["access_token"] == "[REDACTED]"
    assert new_state["jwt"] == "[REDACTED]"
    assert new_state["raw_text"] == "[REDACTED]"
    assert new_state["document_text"] == "[REDACTED]"
    assert new_state["connection_string"] == "[REDACTED]"
