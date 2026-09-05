"""Audit logging service."""

import json
from typing import Any, Optional
from sqlalchemy.orm import Session

from apps.backend.app.models.audit_log import AuditLog

# Event action types
LOGIN_SUCCEEDED = "LOGIN_SUCCEEDED"
LOGIN_FAILED = "LOGIN_FAILED"
AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
CASE_CREATED = "CASE_CREATED"
CASE_UPDATED = "CASE_UPDATED"
CASE_ACCESS_GRANTED = "CASE_ACCESS_GRANTED"
CASE_ACCESS_REVOKED = "CASE_ACCESS_REVOKED"
DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
DOCUMENT_VIEWED = "DOCUMENT_VIEWED"
DOCUMENT_PROCESSED = "DOCUMENT_PROCESSED"
EXTRACTION_STARTED = "EXTRACTION_STARTED"
EXTRACTION_COMPLETED = "EXTRACTION_COMPLETED"
ENTITY_REVIEWED = "ENTITY_REVIEWED"
RELATIONSHIP_REVIEWED = "RELATIONSHIP_REVIEWED"
GRAPH_SYNC_TRIGGERED = "GRAPH_SYNC_TRIGGERED"
GRAPH_ANALYTICS_RUN = "GRAPH_ANALYTICS_RUN"
SIMILARITY_RUN = "SIMILARITY_RUN"
MODEL_INFERENCE_RUN = "MODEL_INFERENCE_RUN"
MODEL_REGISTRY_VIEWED = "MODEL_REGISTRY_VIEWED"
REPORT_GENERATED = "REPORT_GENERATED"
REPORT_EXPORTED = "REPORT_EXPORTED"


def log_action(
    db: Session,
    action: str,
    target_type: str,
    target_id: str,
    user_id: Optional[str] = None,
    rationale: Optional[str] = None,
    previous_state: Optional[dict[str, Any]] = None,
    new_state: Optional[dict[str, Any]] = None,
) -> AuditLog:
    """Record an immutable audit log entry."""
    # Sanitize states: do not log secrets or large text blocks
    sanitized_prev = _sanitize_state(previous_state)
    sanitized_new = _sanitize_state(new_state)

    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        rationale=rationale,
        previous_state=json.dumps(sanitized_prev) if sanitized_prev else None,
        new_state=json.dumps(sanitized_new) if sanitized_new else None,
    )
    
    try:
        db.add(audit_entry)
        db.commit()
    except Exception:
        db.rollback()
        # Ensure audit logging failures do not crash the main transaction
        # or leak stack traces to standard output unexpectedly.
        pass
        
    return audit_entry


def _sanitize_state(state: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Remove sensitive fields from audit payload."""
    if not state:
        return None
    
    sanitized = {}
    sensitive_keys = {
        "password", "password_hash", "access_token", "secret", "content", 
        "raw_text", "jwt", "token", "refresh_token", "authorization", 
        "database_url", "connection_string", "file_path", "internal_path", 
        "stack_trace", "traceback", "raw_evidence", "document_text"
    }
    for k, v in state.items():
        # Substring match for broader safety
        if any(sensitive in k.lower() for sensitive in sensitive_keys):
            sanitized[k] = "[REDACTED]"
        else:
            sanitized[k] = v
    return sanitized
