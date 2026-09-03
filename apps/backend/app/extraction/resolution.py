"""Entity resolution service for extraction candidates."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from apps.backend.app.models.entity import ExtractedEntity

def resolve_entity_candidate(db: Session, case_id: str, normalized_value: str, entity_type: str) -> Dict[str, Any]:
    """
    Look for existing entities in the database matching the normalized value and type.
    Returns resolution metadata.
    """
    matches = db.query(ExtractedEntity).filter(
        ExtractedEntity.case_id == case_id,
        ExtractedEntity.entity_type == entity_type,
        ExtractedEntity.canonical_name == normalized_value
    ).all()

    if not matches:
        return {
            "has_match": False,
            "existing_entity_id": None,
            "match_score": 0.0,
            "match_reasons": [],
            "requires_human_review": False
        }

    # Found a match based on exact canonical name.
    # We could implement fuzzing, but for now exact match is a 1.0.
    best_match = matches[0]
    
    # Example logic: if we match on alias, might want human review.
    # In deterministic synthetic, exact is 1.0.
    requires_review = len(matches) > 1

    return {
        "has_match": True,
        "existing_entity_id": best_match.id,
        "match_score": 1.0,
        "match_reasons": ["Exact canonical_name match"],
        "requires_human_review": requires_review
    }
