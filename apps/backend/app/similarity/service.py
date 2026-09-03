"""Similarity service."""
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import uuid
from datetime import datetime, timezone

from apps.backend.app.models.ml import CaseFeatureVector, SimilarityResult
from .schemas import SimilarityMatch

# Configurable weights for categories
FEATURE_WEIGHTS = {
    # Structural (High weight)
    "graph_density": 2.0,
    "average_betweenness": 2.0,
    "bridge_candidate_count": 2.0,
    "maximum_degree": 1.5,
    "community_count": 1.5,
    
    # Patterns (High weight)
    "cross_case_connector_count": 2.0,
    "rapid_transaction_chain_count": 2.0,
    "shared_phone_pattern_count": 1.5,
    
    # Everything else gets default weight 1.0
}

def calculate_historical_similarity(db: Session, target_case_id: str, top_k: int = 5) -> list[SimilarityMatch]:
    """Calculates weighted deterministic cosine similarity against all historical cases."""
    
    vectors = db.query(CaseFeatureVector).all()
    if not vectors:
        return []

    target_vec = next((v for v in vectors if v.case_id == target_case_id), None)
    if not target_vec:
        return []
        
    other_vecs = [v for v in vectors if v.case_id != target_case_id]
    if not other_vecs:
        return []
        
    feature_names = target_vec.feature_names
    
    # 1. Build matrix
    all_cases = [target_vec] + other_vecs
    raw_matrix = np.array([v.feature_values for v in all_cases])
    
    # 2. Handle missing/NaN deterministically
    raw_matrix = np.nan_to_num(raw_matrix, nan=0.0)
    
    # 3. Normalize (Divide by max to scale to [0,1] without shifting zero)
    max_vals = np.max(raw_matrix, axis=0)
    # Avoid division by zero for features that are all 0
    max_vals[max_vals == 0] = 1.0 
    normalized_matrix = raw_matrix / max_vals
    
    # 4. Apply weights
    weights = np.array([FEATURE_WEIGHTS.get(name, 1.0) for name in feature_names])
    weighted_matrix = normalized_matrix * weights
    
    target_norm = weighted_matrix[0].reshape(1, -1)
    others_norm = weighted_matrix[1:]
    
    # 5. Calculate Cosine Similarity
    similarities = cosine_similarity(target_norm, others_norm)[0]
    
    results = []
    for i, score in enumerate(similarities):
        other = other_vecs[i]
        
        # Calculate matched and differing features
        diffs = np.abs(normalized_matrix[0] - normalized_matrix[i + 1])
        sorted_indices = np.argsort(diffs)
        
        # Top 3 most similar (smallest diff) and least similar (largest diff)
        matched = {feature_names[idx]: float(raw_matrix[i+1][idx]) for idx in sorted_indices[:3] if diffs[idx] < 0.2}
        differing = {feature_names[idx]: float(raw_matrix[i+1][idx]) for idx in sorted_indices[-3:] if diffs[idx] > 0.4}
        
        explanation_parts = []
        if matched:
            explanation_parts.append(f"both share similar structural indicators like {', '.join(matched.keys())}")
        
        explanation = (
            f"This case has structural similarity to {other.case_id} because " +
            (explanation_parts[0] if explanation_parts else "of overall structural and volumetric resemblance.") +
            " Similarity does not establish that the cases are the same."
        )

        results.append((score, other, matched, differing, explanation))
        
    # 6. Tie-breaking (score descending, case_id ascending)
    results.sort(key=lambda x: (-x[0], x[1].case_id))
    results = results[:top_k]
    
    matches = []
    run_id = str(uuid.uuid4())
    
    for score, other, matched, differing, explanation in results:
        # Persist result
        sr = SimilarityResult(
            id=str(uuid.uuid4()),
            current_case_id=target_case_id,
            similar_case_id=other.case_id,
            similarity_score=float(score),
            matched_features=matched,
            differing_features=differing,
            explanation=explanation,
            feature_version=target_vec.feature_version,
            analysis_run_id=run_id
        )
        db.add(sr)
        
        matches.append(SimilarityMatch(
            current_case_id=target_case_id,
            similar_case_id=other.case_id,
            similarity_score=float(score),
            matched_features=matched,
            differing_features=differing,
            explanation=explanation,
            feature_version=target_vec.feature_version,
            analysis_run_id=run_id,
            computed_at=datetime.now(timezone.utc)
        ))
    
    db.commit()
    return matches
