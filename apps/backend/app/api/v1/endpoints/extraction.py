"""API endpoints for NLP Document Extraction."""
import os
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from apps.backend.app.db.session import get_db
from apps.backend.app.extraction.service import DocumentExtractionService
from apps.backend.app.extraction.schemas import ReviewDecision

router = APIRouter()

def get_reviewer_id():
    # Use DEV_REVIEWER_ID or a mock ID until auth is added
    return os.getenv("DEV_REVIEWER_ID", "DEV-USER-001")

@router.post("/documents/{document_id}/extract")
def extract_document(document_id: str, db: Session = Depends(get_db)):
    svc = DocumentExtractionService(db)
    try:
        res = svc.process_document(document_id)
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/documents/{document_id}/extraction-candidates")
def get_extraction_candidates(document_id: str, db: Session = Depends(get_db)):
    from apps.backend.app.models.entity import ExtractedEntity
    from apps.backend.app.models.relationship import ExtractedRelationship
    
    entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == document_id).all()
    relationships = db.query(ExtractedRelationship).filter(ExtractedRelationship.document_id == document_id).all()
    
    return {
        "entities": [
            {
                "id": e.id,
                "entity_type": e.entity_type,
                "original_value": e.original_value,
                "normalized_value": e.canonical_name,
                "source_text": e.source_text,
                "start_offset": e.start_offset,
                "end_offset": e.end_offset,
                "confidence": e.confidence_score,
                "verification_status": e.verification_status,
                "extraction_provider": e.extraction_provider,
                "extraction_version": e.extraction_version,
            } for e in entities
        ],
        "relationships": [
            {
                "id": r.id,
                "source_entity_id": r.source_entity_id,
                "target_entity_id": r.target_entity_id,
                "relation_type": r.relation_type,
                "source_text": r.source_text_snippet,
                "confidence": r.confidence_score,
                "verification_status": r.verification_status,
                "extraction_provider": r.extraction_provider,
                "extraction_version": r.extraction_version,
            } for r in relationships
        ]
    }

@router.get("/documents/{document_id}/extraction-status")
def get_extraction_status(document_id: str, db: Session = Depends(get_db)):
    # Returns count of pending vs verified
    from apps.backend.app.models.entity import ExtractedEntity
    
    total = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == document_id).count()
    unreviewed = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == document_id, 
        ExtractedEntity.verification_status == "UNREVIEWED"
    ).count()
    
    return {
        "total_candidates": total,
        "unreviewed_candidates": unreviewed,
        "is_complete": total > 0 and unreviewed == 0
    }

@router.post("/extraction-candidates/{candidate_type}/{candidate_id}/review")
def review_candidate(
    candidate_type: str, 
    candidate_id: str, 
    decision: ReviewDecision, 
    db: Session = Depends(get_db)
):
    svc = DocumentExtractionService(db)
    reviewer_id = get_reviewer_id()
    try:
        if candidate_type == "entity":
            svc.review_entity(candidate_id, decision, reviewer_id)
        elif candidate_type == "relationship":
            svc.review_relationship(candidate_id, decision, reviewer_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid candidate type")
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/documents/{document_id}/sync-approved")
def sync_approved(document_id: str, db: Session = Depends(get_db)):
    svc = DocumentExtractionService(db)
    res = svc.sync_approved_to_graph(document_id)
    return res

@router.post("/documents/{document_id}/extract-and-review-preview")
def extract_and_review_preview(document_id: str, db: Session = Depends(get_db)):
    """Preview what would be extracted without persisting."""
    from apps.backend.app.models.document import Document
    from apps.backend.app.extraction.mock_provider import MockExtractor
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    extractor = MockExtractor()
    result = extractor.extract(document_id, doc.content)
    
    return result.model_dump()
