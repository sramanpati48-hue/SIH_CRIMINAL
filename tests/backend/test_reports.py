"""Tests for report generation and export."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case import Case
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.services.audit import REPORT_EXPORTED

@pytest.fixture
def sample_case(db_session: Session, test_users: dict[str, User]) -> Case:
    case = Case(
        case_number="REP-001",
        title="Report Test Case",
        status="ACTIVE",
        priority="MEDIUM",
        created_by=test_users["INVESTIGATOR"].id
    )
    db_session.add(case)
    db_session.flush()

    # Assign access to test_investigator
    access = CaseAccess(
        user_id=test_users["INVESTIGATOR"].id,
        case_id=case.id,
        access_level=CaseAccessLevel.VIEW.value,
        assigned_by_user_id=test_users["ADMINISTRATOR"].id,
        is_active=True
    )
    db_session.add(access)

    # Entities
    e1 = ExtractedEntity(
        case_id=case.id,
        entity_type="PERSON",
        original_value="John Doe",
        canonical_name="John Doe",
        verification_status="ACCEPTED",
        confidence_score=0.9
    )
    e2 = ExtractedEntity(
        case_id=case.id,
        entity_type="PERSON",
        original_value="Jane Smith",
        canonical_name="Jane Smith",
        verification_status="REJECTED",
        confidence_score=0.4
    )
    e3 = ExtractedEntity(
        case_id=case.id,
        entity_type="PHONE",
        original_value="555-0101",
        canonical_name="555-0101",
        verification_status="CORRECTED",
        confidence_score=0.8
    )
    db_session.add_all([e1, e2, e3])
    db_session.flush()

    # Relationship
    r1 = ExtractedRelationship(
        case_id=case.id,
        source_entity_id=e1.id,
        target_entity_id=e3.id,
        relation_type="OWNS_PHONE",
        verification_status="ACCEPTED",
        confidence_score=0.85,
        source_text_snippet="John Doe called from 555-0101.",
    )
    r2 = ExtractedRelationship(
        case_id=case.id,
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relation_type="KNOWS",
        verification_status="REJECTED",
        confidence_score=0.3,
        source_text_snippet="John knows Jane."
    )
    db_session.add_all([r1, r2])
    db_session.commit()
    db_session.refresh(case)
    return case


def test_unauthenticated_report_request(unauthenticated_client: TestClient, sample_case: Case):
    """Test that unauthenticated request returns 401."""
    response = unauthenticated_client.get(f"/api/v1/cases/{sample_case.id}/report/html")
    assert response.status_code == 401


def test_unauthorized_report_request(unauthenticated_client: TestClient, db_session: Session, sample_case: Case, test_users: dict[str, User]):
    """Test that user without case access returns 403."""
    # Create another user
    u2 = User(username="other_investigator", email="other@example.com", password_hash="hash", role=Role.INVESTIGATOR.value, is_active=True)
    db_session.add(u2)
    db_session.commit()
    db_session.refresh(u2)

    from apps.backend.app.core.security import create_access_token
    token = create_access_token(u2.id)
    
    response = unauthenticated_client.get(
        f"/api/v1/cases/{sample_case.id}/report/html",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_successful_html_report_export(unauthenticated_client: TestClient, db_session: Session, sample_case: Case, test_users: dict[str, User]):
    """Test successful export with valid access."""
    # test_investigator has access
    from apps.backend.app.core.security import create_access_token
    token = create_access_token(test_users["INVESTIGATOR"].id)
    
    response = unauthenticated_client.get(
        f"/api/v1/cases/{sample_case.id}/report/html",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # Headers
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert "attachment; filename=\"case-report-" in response.headers["Content-Disposition"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"
    
    html = response.text
    
    # Content Checks
    assert "SIH 26189 — Investigation Support Report" in html
    assert "John Doe" in html
    assert "555-0101" in html
    assert "John Doe called from 555-0101." in html
    
    # Rejected entities and relationships should be excluded
    assert "Jane Smith" not in html
    assert "John knows Jane" not in html
    
    # CSP Check
    assert "Content-Security-Policy" in html
    assert "default-src 'none'" in html
    
    # Audit log check
    audit_logs = db_session.query(AuditLog).filter(AuditLog.target_id == sample_case.id).all()
    export_logs = [log for log in audit_logs if log.action == REPORT_EXPORTED]
    assert len(export_logs) == 1
    
    import json
    metadata = json.loads(export_logs[0].new_state) if export_logs[0].new_state else {}
    assert "report_generated" in metadata
    assert "report_version" in metadata
    
def test_admin_can_export(unauthenticated_client: TestClient, db_session: Session, sample_case: Case, test_users: dict[str, User]):
    """Test administrator can export even without explicit case access mapping."""
    from apps.backend.app.core.security import create_access_token
    token = create_access_token(test_users["ADMINISTRATOR"].id)
    
    response = unauthenticated_client.get(
        f"/api/v1/cases/{sample_case.id}/report/html",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
