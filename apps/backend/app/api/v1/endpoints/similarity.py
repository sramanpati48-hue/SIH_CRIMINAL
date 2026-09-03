"""API Endpoints for Case Similarity."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from apps.backend.app.db.session import get_db
from apps.backend.app.models.case import Case
from apps.backend.app.similarity.features import extract_case_features
from apps.backend.app.similarity.service import calculate_historical_similarity
from apps.backend.app.similarity.schemas import SimilarityResponse, FeatureVectorResponse
from apps.backend.app.models.ml import CaseFeatureVector, SimilarityResult

router = APIRouter()

@router.post("/{case_id}/similarity", response_model=SimilarityResponse)
def compute_similarity(
    case_id: str,
    top_k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Computes similarity for a case and returns top-k similar cases."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    run_id = str(uuid.uuid4())
    
    # 1. Ensure feature vector exists and is up-to-date
    extract_case_features(db, case_id, run_id)
    
    # 2. Extract for all other cases that might not have vectors (in a real scenario, this is async)
    all_cases = db.query(Case).all()
    existing_vecs = {v.case_id for v in db.query(CaseFeatureVector).all()}
    for c in all_cases:
        if c.id not in existing_vecs:
            extract_case_features(db, c.id, run_id)
            
    # 3. Calculate similarity
    matches = calculate_historical_similarity(db, case_id, top_k)
    
    return SimilarityResponse(results=matches)

@router.get("/{case_id}/similarity", response_model=SimilarityResponse)
def get_similarity(
    case_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Retrieves already computed similarity results."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    results = db.query(SimilarityResult).filter(
        SimilarityResult.current_case_id == case_id
    ).order_by(SimilarityResult.similarity_score.desc()).limit(limit).all()
    
    # Mapping to schema
    matches = []
    for r in results:
        matches.append({
            "current_case_id": r.current_case_id,
            "similar_case_id": r.similar_case_id,
            "similarity_score": r.similarity_score,
            "matched_features": r.matched_features or {},
            "differing_features": r.differing_features or {},
            "explanation": r.explanation,
            "feature_version": r.feature_version,
            "analysis_run_id": r.analysis_run_id,
            "computed_at": r.created_at
        })

    return SimilarityResponse(results=matches)

@router.get("/{case_id}/features", response_model=FeatureVectorResponse)
def get_feature_vector(
    case_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves the latest feature vector for a case."""
    vec = db.query(CaseFeatureVector).filter(CaseFeatureVector.case_id == case_id).order_by(CaseFeatureVector.created_at.desc()).first()
    if not vec:
        raise HTTPException(status_code=404, detail="Feature vector not found")
        
    return {
        "case_id": vec.case_id,
        "feature_names": vec.feature_names,
        "feature_values": vec.feature_values,
        "feature_version": vec.feature_version,
        "generated_at": vec.created_at,
        "source_analysis_run_id": vec.analysis_run_id
    }
