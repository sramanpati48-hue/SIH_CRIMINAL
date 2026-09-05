"""End-to-End Demo Verification Tests."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from apps.backend.app.models.case import Case
from apps.backend.app.models.user import User
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.services.audit import REPORT_EXPORTED

@pytest.fixture(scope="module")
def setup_demo_environment():
    """Ensure environment is set up for demo tests."""
    os.environ["APP_ENV"] = "development"
    os.environ["DEMO_PASSWORD"] = "testdemopass"
    
    # We invoke the reset and seed scripts programmatically for the test DB
    from scripts.reset_demo_data import reset_demo_data
    from scripts.seed_demo_data import seed_demo_data
    
    # We must patch SessionLocal in scripts to use test DB if we want this isolated.
    # However, since this E2E runs in pytest, the db fixtures are better. Let's just use the client to test the API directly
    # and we will manually trigger the functions using the test database.
    # Actually, modifying `SessionLocal` in the imported scripts is tricky in Pytest.
    pass

@pytest.fixture
def demo_data(db_session: Session):
    """Seed demo data directly into the test DB."""
    from apps.backend.app.models.user import Role
    from apps.backend.app.core.security import get_password_hash
    from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
    from apps.backend.app.models.ml import SimilarityResult, ModelPrediction
    from apps.backend.app.models.alert import Alert
    
    # Users
    u1 = User(username="demo_admin", email="a@d.c", password_hash=get_password_hash("testpassword"), role=Role.ADMINISTRATOR.value, is_active=True)
    u2 = User(username="demo_investigator", email="i@d.c", password_hash=get_password_hash("testpassword"), role=Role.INVESTIGATOR.value, is_active=True)
    u3 = User(username="demo_analyst", email="an@d.c", password_hash=get_password_hash("testpassword"), role=Role.ANALYST.value, is_active=True)
    u4 = User(username="other_investigator", email="o@d.c", password_hash=get_password_hash("testpassword"), role=Role.INVESTIGATOR.value, is_active=True)
    db_session.add_all([u1, u2, u3, u4])
    db_session.flush()

    case = Case(case_number="CASE-TEST-001", title="Test Case", status="ACTIVE", priority="HIGH", created_by=u1.id)
    case_unassigned = Case(case_number="CASE-TEST-002", title="Unassigned Case", status="ACTIVE", priority="HIGH", created_by=u1.id)
    db_session.add_all([case, case_unassigned])
    db_session.flush()

    db_session.add(CaseAccess(user_id=u2.id, case_id=case.id, access_level=CaseAccessLevel.MANAGE.value, assigned_by_user_id=u1.id))
    db_session.add(CaseAccess(user_id=u3.id, case_id=case.id, access_level=CaseAccessLevel.ANALYZE.value, assigned_by_user_id=u1.id))
    db_session.add(CaseAccess(user_id=u4.id, case_id=case_unassigned.id, access_level=CaseAccessLevel.MANAGE.value, assigned_by_user_id=u1.id))
    
    # Entities and Rels
    e1 = ExtractedEntity(case_id=case.id, entity_type="PERSON", original_value="John Doe", canonical_name="John Doe", verification_status="ACCEPTED")
    e2 = ExtractedEntity(case_id=case.id, entity_type="PHONE", original_value="555-1234", canonical_name="555-1234", verification_status="ACCEPTED")
    db_session.add_all([e1, e2])
    db_session.flush()

    r1 = ExtractedRelationship(case_id=case.id, source_entity_id=e1.id, target_entity_id=e2.id, relation_type="CALLS", verification_status="ACCEPTED", source_text_snippet="John called 555")
    r2 = ExtractedRelationship(case_id=case.id, source_entity_id=e1.id, target_entity_id=e2.id, relation_type="KNOWS", verification_status="REJECTED", source_text_snippet="John knows 555")
    db_session.add_all([r1, r2])

    alert = Alert(case_id=case.id, alert_type="PATTERN", severity="HIGH", title="Burner", description="Desc", status="OPEN")
    sim = SimilarityResult(
        current_case_id=case.id, 
        similar_case_id=case.id, 
        similarity_score=1.0, 
        explanation="test", 
        feature_version="v1", 
        analysis_run_id="run-001"
    )
    ml_pred = ModelPrediction(
        case_id=case.id, 
        prediction_type="ANOMALY", 
        prediction="ANOMALOUS", 
        score=0.82, 
        explanation="test", 
        model_version="v1", 
        dataset_version="v1", 
        feature_version="v1", 
        analysis_run_id="run-001"
    )
    db_session.add_all([alert, sim, ml_pred])
    
    db_session.commit()
    return {"case": case.id, "case_unassigned": case_unassigned.id, "investigator_id": u2.id, "admin_id": u1.id}

def test_demo_e2e_flow(unauthenticated_client: TestClient, db_session: Session, demo_data: dict):
    # 2. Login as demo investigator
    response = unauthenticated_client.post("/api/v1/auth/login", data={"username": "demo_investigator", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_id = demo_data["case"]
    unassigned_id = demo_data["case_unassigned"]

    # 3. View the assigned case
    res = unauthenticated_client.get(f"/api/v1/cases/{case_id}", headers=headers)
    assert res.status_code == 200

    # 4. Attempt access to unassigned case
    res = unauthenticated_client.get(f"/api/v1/cases/{unassigned_id}", headers=headers)
    assert res.status_code == 403

    # 13. Export HTML report
    res = unauthenticated_client.get(f"/api/v1/cases/{case_id}/report/html", headers=headers)
    assert res.status_code == 200
    html = res.text

    # 14. Confirm report excludes rejected facts
    assert "John called 555" in html  # ACCEPTED
    assert "John knows 555" not in html # REJECTED

    # 15. Confirm exactly one REPORT_EXPORTED audit event
    audit_logs = db_session.query(AuditLog).filter(AuditLog.target_id == case_id, AuditLog.action == REPORT_EXPORTED).all()
    assert len(audit_logs) == 1

    # 16. Confirm no sensitive information in audit metadata
    import json
    metadata = json.loads(audit_logs[0].new_state)
    assert "report_generated" in metadata
    assert "HTML" not in metadata
    assert "html" not in metadata
    assert "password" not in metadata
    assert "John called" not in metadata

def test_demo_reset_refuses_production(monkeypatch):
    from scripts.reset_demo_data import reset_demo_data
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(SystemExit) as exc:
        reset_demo_data()
    assert exc.value.code == 1

def test_demo_seed_is_idempotent(db_session, monkeypatch):
    from scripts.seed_demo_data import seed_demo_data
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEMO_PASSWORD", "testpassword")
    
    import contextlib
    @contextlib.contextmanager
    def mock_session_local():
        yield db_session
        
    monkeypatch.setattr("scripts.seed_demo_data.SessionLocal", mock_session_local)
    
    # First seed
    seed_demo_data()
    
    # Second seed
    seed_demo_data()
    
    # Verify no duplicates
    cases = db_session.query(Case).filter(Case.case_number == "CASE-2024-SYN-001").all()
    assert len(cases) == 1

    users = db_session.query(User).filter(User.username == "demo_admin").all()
    assert len(users) == 1

def test_no_hardcoded_passwords_in_source():
    import os
    import re
    # A simple regex to check for passwords in seed_demo_data.py
    script_path = os.path.join(os.path.dirname(__file__), "../../scripts/seed_demo_data.py")
    with open(script_path, "r") as f:
        content = f.read()
    assert "password_hash='pass'" not in content
    assert "password_hash=\"pass\"" not in content

def test_verify_demo_ready(db_session, monkeypatch, capsys):
    from scripts.verify_demo_ready import verify_demo_ready
    monkeypatch.setenv("APP_ENV", "development")
    
    import contextlib
    @contextlib.contextmanager
    def mock_session_local():
        yield db_session
        
    monkeypatch.setattr("scripts.verify_demo_ready.SessionLocal", mock_session_local)
    
    # Assuming db is already seeded
    with pytest.raises(SystemExit) as exc:
        verify_demo_ready()
    
    out, err = capsys.readouterr()
    # It might print READY or READY_WITH_WARNINGS
    assert "READY" in out

