"""Similarity Schemas."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class FeatureVectorResponse(BaseModel):
    case_id: str
    feature_names: List[str]
    feature_values: List[float]
    feature_version: str
    generated_at: datetime
    source_analysis_run_id: str


class SimilarityMatch(BaseModel):
    current_case_id: str
    similar_case_id: str
    similarity_score: float
    matched_features: Dict[str, Any]
    differing_features: Dict[str, Any]
    explanation: str
    feature_version: str
    analysis_run_id: str
    computed_at: datetime


class SimilarityResponse(BaseModel):
    results: List[SimilarityMatch]
    provider: str = "feature_vector"
    warning: Optional[str] = "Deterministic engineered features used; graph embeddings unavailable"
