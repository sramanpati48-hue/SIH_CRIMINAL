"""API endpoints for NLP Document Extraction."""
import re
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from apps.backend.app.core.config import settings
from apps.backend.app.db.session import get_db
from apps.backend.app.extraction.service import DocumentExtractionService
from apps.backend.app.extraction.schemas import ReviewDecision

router = APIRouter()


def get_reviewer_id() -> str:
    """Return the configured development reviewer identity from settings.

    Raises:
        HTTPException 503: when DEV_REVIEWER_ID is not set, making the
            misconfiguration visible immediately rather than silently writing
            an empty or hardcoded identity into audit logs.

    Note:
        Authentication is NOT enabled in this milestone.  This function
        exists solely to ensure the reviewer identity comes from
        configuration, never from a literal string in application logic.
    """
    reviewer_id = settings.DEV_REVIEWER_ID
    if not reviewer_id:
        raise HTTPException(
            status_code=503,
            detail=(
                "DEV_REVIEWER_ID is not configured.  "
                "Set it in apps/backend/.env before submitting review actions.  "
                "Authentication is not enabled in this milestone."
            ),
        )
    return reviewer_id


@router.get("/review-session")
def get_review_session() -> Dict[str, Any]:
    """Return current reviewer session metadata (development mode only).

    Returns the configured reviewer identity and a warning that no
    authentication is active.  The frontend uses this to display the
    development-reviewer-mode banner.  This endpoint must never claim
    that authentication is enabled.
    """
    reviewer_id = settings.DEV_REVIEWER_ID
    return {
        "reviewer_mode": "DEV",
        "reviewer_id": reviewer_id,
        "authentication_enabled": False,
        "warning": (
            "This session uses a development reviewer identity configured "
            "via DEV_REVIEWER_ID.  Authentication is not enabled.  "
            "All review actions are recorded in audit logs with this identity."
        ),
    }


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

    entities = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == document_id
    ).all()
    relationships = db.query(ExtractedRelationship).filter(
        ExtractedRelationship.document_id == document_id
    ).all()

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
            }
            for e in entities
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
            }
            for r in relationships
        ],
    }


@router.get("/health")
def get_extraction_health() -> Dict[str, Any]:
    """Return extraction provider health and availability."""
    from apps.backend.app.extraction.mock_provider import MockExtractor
    from apps.backend.app.extraction.local_ner_provider import SpacyNERProvider
    
    mock = MockExtractor()
    providers = []
    
    providers.append({
        "name": mock.provider_name,
        "status": "AVAILABLE",
        "provider_version": mock.provider_version,
        "model_version": mock.model_version
    })
    
    spacy = SpacyNERProvider()
    if getattr(spacy, "_is_available", False):
        spacy_status = "AVAILABLE"
        reason = None
    else:
        spacy_status = "UNAVAILABLE"
        reason = "spaCy model en_core_web_sm not downloaded or spacy not installed."
        
    providers.append({
        "name": spacy.provider_name,
        "status": spacy_status,
        "provider_version": spacy.provider_version,
        "model_version": spacy.model_version if spacy_status == "AVAILABLE" else "N/A",
        "reason": reason
    })
    
    return {"providers": providers}


@router.get("/documents/{document_id}/extraction-runs")
def get_extraction_runs(document_id: str, db: Session = Depends(get_db)):
    """Get history of extraction runs for a document."""
    from apps.backend.app.models.extraction_run import ExtractionRun
    
    runs = db.query(ExtractionRun).filter(ExtractionRun.document_id == document_id).order_by(ExtractionRun.created_at.desc()).all()
    
    return {
        "runs": [
            {
                "extraction_run_id": r.extraction_run_id,
                "provider": r.provider,
                "provider_version": r.provider_version,
                "model_version": r.model_version,
                "status": r.status,
                "entity_candidate_count": r.entity_candidate_count,
                "relationship_candidate_count": r.relationship_candidate_count,
                "warnings": r.warnings,
                "started_at": r.started_at,
                "completed_at": r.completed_at
            }
            for r in runs
        ]
    }


@router.post("/documents/{document_id}/compare-providers")
def api_compare_providers(document_id: str, providers: List[str], db: Session = Depends(get_db)):
    """Compare providers on a single document in memory."""
    from apps.backend.app.models.document import Document
    from apps.backend.app.evaluation.provider_comparison import compare_providers
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    res = compare_providers(
        providers=providers,
        documents=[{"id": doc.id, "text": doc.raw_content or ""}],
        gold_entities=[],
        gold_relationships=[],
        dataset_version="user_doc"
    )
    
    return res.model_dump()


@router.get("/evaluation-metadata")
def get_evaluation_metadata():
    """Metadata about the synthetic test dataset."""
    import os
    import json
    
    test_path = "data/synthetic/ner/test.jsonl"
    count = 0
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as f:
            count = sum(1 for line in f if line.strip())
            
    return {
        "dataset_version": "v1.0-synthetic",
        "document_count": count,
        "description": "Deterministic synthetic evaluation dataset for Milestone 10.",
        "splits": ["test"]
    }


@router.post("/evaluate")
def api_evaluate_extraction(providers: List[str] = ["MOCK"]):
    """Evaluate specified providers against the synthetic test set."""
    from apps.backend.app.evaluation.provider_comparison import compare_providers
    import os
    import json
    
    test_path = "data/synthetic/ner/test.jsonl"
    if not os.path.exists(test_path):
        raise HTTPException(status_code=404, detail="Synthetic test dataset not found.")
        
    documents = []
    gold_entities = []
    gold_relationships = []
    
    with open(test_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            doc = json.loads(line)
            documents.append(doc)
            doc_id = doc.get("id", doc.get("document_id"))
            for ent in doc.get("entities", []):
                ent["document_id"] = doc_id
                gold_entities.append(ent)
            for rel in doc.get("relationships", []):
                rel["document_id"] = doc_id
                gold_relationships.append(rel)
                
    res = compare_providers(
        providers=providers,
        documents=documents,
        gold_entities=gold_entities,
        gold_relationships=gold_relationships,
        dataset_version="v1.0-synthetic"
    )
    
    return res.model_dump()


@router.get("/documents/{document_id}/extraction-status")
def get_extraction_status(document_id: str, db: Session = Depends(get_db)):
    from apps.backend.app.models.entity import ExtractedEntity

    total = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == document_id
    ).count()
    unreviewed = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == document_id,
        ExtractedEntity.verification_status == "UNREVIEWED",
    ).count()

    return {
        "total_candidates": total,
        "unreviewed_candidates": unreviewed,
        "is_complete": total > 0 and unreviewed == 0,
    }


@router.post("/extraction-candidates/{candidate_type}/{candidate_id}/review")
def review_candidate(
    candidate_type: str,
    candidate_id: str,
    decision: ReviewDecision,
    db: Session = Depends(get_db),
):
    svc = DocumentExtractionService(db)
    reviewer_id = get_reviewer_id()  # Raises 503 if unconfigured
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


@router.post("/documents/{document_id}/extract-relationships")
def extract_relationships(document_id: str, db: Session = Depends(get_db)):
    from apps.backend.app.models.document import Document
    from apps.backend.app.models.entity import ExtractedEntity
    from apps.backend.app.extraction.relationship_service import RelationshipExtractionService
    from apps.backend.app.extraction.schemas import ExtractedEntityCandidate
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db_entities = db.query(ExtractedEntity).filter_by(document_id=document_id).all()
    entities = [
        ExtractedEntityCandidate(
            candidate_id=e.id, # Map DB id as candidate_id
            entity_type=e.entity_type,
            original_value=e.original_value or "",
            normalized_value=e.canonical_name,
            source_document_id=document_id,
            source_text=doc.content or e.source_text or "",
            start_offset=e.start_offset or 0,
            end_offset=e.end_offset or 0,
            confidence=float(e.confidence_score) if e.confidence_score else 0.85,
            verification_status=e.verification_status,
            extraction_provider=e.extraction_provider or "UNKNOWN",
            extraction_version=e.extraction_version or "1.0"
        )
        for e in db_entities if e.start_offset is not None and e.end_offset is not None
    ]
    
    provider = settings.EXTRACTION_PROVIDER
    svc = RelationshipExtractionService(db, provider, "1.0")
    candidates = svc.extract_relationships(document_id, doc.case_id, doc.content or "", entities)
    persisted = svc.persist_candidates(candidates)
    
    return {
        "document_id": document_id,
        "extracted_count": len(candidates),
        "persisted_count": len(persisted)
    }

@router.get("/documents/{document_id}/relationship-candidates")
def get_relationship_candidates(document_id: str, db: Session = Depends(get_db)):
    from apps.backend.app.models.relationship import ExtractedRelationship
    relationships = db.query(ExtractedRelationship).filter(
        ExtractedRelationship.document_id == document_id
    ).all()
    
    return {
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
                "relationship_rule_version": r.relationship_rule_version
            }
            for r in relationships
        ]
    }

@router.post("/documents/{document_id}/sync-approved-relationships")
def sync_approved_relationships(document_id: str, db: Session = Depends(get_db)):
    from apps.backend.app.extraction.service import DocumentExtractionService
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


# ---------------------------------------------------------------------------
# Model ID format validator (shared by all model registry endpoints)
# ---------------------------------------------------------------------------

_MODEL_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,100}$')


def _validate_model_id_param(model_id: str) -> None:
    """Raise 422 if model_id contains invalid characters or path components."""
    if not model_id or not _MODEL_ID_PATTERN.match(model_id):
        raise HTTPException(
            status_code=422,
            detail={
                "status": "ARTIFACT_PATH_REJECTED",
                "message": "model_id must contain only alphanumeric characters, "
                           "hyphens, or underscores (max 100 chars).",
            },
        )


# ---------------------------------------------------------------------------
# Training readiness
# ---------------------------------------------------------------------------

@router.get("/extraction/training-readiness")
def get_training_readiness() -> Dict[str, Any]:
    """Return readiness status for custom NER fine-tuning.

    Data directory is read from server configuration, never from the request.
    This endpoint does not trigger training or model downloads.
    Development-only until authentication is enabled.
    """
    import os
    from apps.backend.app.training.readiness import check_training_readiness
    data_dir = "data/synthetic/ner"  # Server-controlled path only
    status = check_training_readiness(data_dir=data_dir)
    result = status.model_dump()
    # Ensure no path fields leak into the response
    result.pop("data_dir", None)
    return result


# ---------------------------------------------------------------------------
# Model registry listing
# ---------------------------------------------------------------------------

@router.get("/extraction/models")
def list_extraction_models(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """List registered extraction models.

    Returns safe public metadata only. Does not include filesystem paths,
    storage keys, artifact filenames, or checksums.
    Development-only until authentication is enabled.
    """
    from apps.backend.app.models.extraction_model import ExtractionModel

    models = (
        db.query(ExtractionModel)
        .order_by(ExtractionModel.created_at.desc())
        .all()
    )
    return [
        {
            "model_id": m.model_id,
            "provider": m.provider,
            "model_type": m.model_type,
            "model_version": m.model_version,
            "dataset_version": m.dataset_version,
            "extraction_version": m.extraction_version,
            "label_schema_version": m.label_schema_version,
            "status": m.status,
            "spacy_version": m.spacy_version,
            "python_version": m.python_version,
            "created_at": m.created_at,
        }
        for m in models
    ]


# ---------------------------------------------------------------------------
# Model registry detail
# ---------------------------------------------------------------------------

@router.get("/extraction/models/{model_id}")
def get_extraction_model(
    model_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get public metadata for a specific model by registry model_id.

    Returns structured status on failure.  Never returns filesystem paths,
    storage keys, checksums, or artifact filenames.
    """
    _validate_model_id_param(model_id)
    from apps.backend.app.models.extraction_model import ExtractionModel

    model = (
        db.query(ExtractionModel)
        .filter(ExtractionModel.model_id == model_id)
        .first()
    )
    if not model:
        raise HTTPException(
            status_code=404,
            detail={"status": "MODEL_NOT_FOUND", "model_id": model_id},
        )

    return {
        "model_id": model.model_id,
        "provider": model.provider,
        "model_type": model.model_type,
        "model_version": model.model_version,
        "dataset_version": model.dataset_version,
        "extraction_version": model.extraction_version,
        "label_schema_version": model.label_schema_version,
        "status": model.status,
        "spacy_version": model.spacy_version,
        "python_version": model.python_version,
        "created_at": model.created_at,
        # Note: artifact_storage_key, artifact_filename, sha256_checksum are
        # intentionally excluded from this response.
    }


# ---------------------------------------------------------------------------
# Model metrics
# ---------------------------------------------------------------------------

@router.get("/extraction/models/{model_id}/metrics")
def get_extraction_model_metrics(
    model_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get held-out evaluation metrics for a specific model.

    Returns structured status on failure.  Never returns filesystem paths.
    """
    _validate_model_id_param(model_id)
    from apps.backend.app.models.extraction_model import ExtractionModel

    model = (
        db.query(ExtractionModel)
        .filter(ExtractionModel.model_id == model_id)
        .first()
    )
    if not model:
        raise HTTPException(
            status_code=404,
            detail={"status": "MODEL_NOT_FOUND", "model_id": model_id},
        )

    return {
        "model_id": model.model_id,
        "status": model.status,
        "training_metrics": model.training_metrics or {},
        "test_metrics": model.test_metrics or {},
        "label_distribution": model.label_distribution or {},
    }

