import pytest
from sqlalchemy.orm import Session
from apps.backend.app.extraction.service import DocumentExtractionService
from apps.backend.app.extraction.schemas import ReviewDecision
from apps.backend.app.models.document import Document
from apps.backend.app.models.case import Case
from apps.backend.app.models.entity import ExtractedEntity

def test_extraction_pipeline_end_to_end(db_session: Session):
    # Setup test case and doc
    c = Case(id="case-1", case_number="C1", title="C1", status="OPEN", priority="LOW")
    db_session.add(c)
    doc = Document(id="doc-1", case_id="case-1", file_name="Rep", raw_content="John Doe called (555) 123-4567.", file_type="TEXT_REPORT")
    db_session.add(doc)
    db_session.commit()

    svc = DocumentExtractionService(db_session)
    
    # 1. Process document
    res = svc.process_document("doc-1")
    assert res["status"] == "success"
    assert res["entities"] > 0
    
    # Verify UNREVIEWED state
    entities = db_session.query(ExtractedEntity).filter_by(document_id="doc-1").all()
    assert len(entities) > 0
    for e in entities:
        assert e.verification_status == "UNREVIEWED"
        
    person_id = [e.id for e in entities if e.entity_type == "PERSON"][0]

    # 2. Review candidate
    decision = ReviewDecision(verification_status="ACCEPTED")
    svc.review_entity(person_id, decision, "DEV-USER-001")
    
    updated = db_session.query(ExtractedEntity).filter_by(id=person_id).first()
    assert updated.verification_status == "ACCEPTED"
    assert updated.reviewer_identity == "DEV-USER-001"

    # 3. Sync approved
    sync_res = svc.sync_approved_to_graph("doc-1")
    # Will be RETRYABLE_FAILURE if Neo4j is offline, or SUCCESS if online
    assert sync_res["status"] in ["SUCCESS", "RETRYABLE_FAILURE"]
    
    db_session.refresh(updated)
    assert updated.graph_sync_status in ["SYNCED", "RETRYABLE_FAILURE"]
