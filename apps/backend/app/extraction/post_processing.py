"""Post-processing logic for extraction results."""

import hashlib
from typing import List, Optional
from apps.backend.app.extraction.schemas import ExtractedEntityCandidate

POST_PROCESSING_VERSION = "1.0.0"

# Target types for post-processing hardening
HARDENED_TYPES = {"PHONE", "VEHICLE", "BANK_ACCOUNT", "CASE_ID", "DATE", "MONEY", "ALIAS"}

def generate_stable_candidate_id(
    source_document_id: str,
    start_offset: int,
    end_offset: int,
    entity_type: str,
    original_value: str
) -> str:
    """Generate a stable, deterministic candidate ID."""
    unique_string = f"{source_document_id}|{start_offset}|{end_offset}|{entity_type}|{original_value}"
    hash_digest = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()[:16]
    return f"ent_{hash_digest}"


def post_process_entities(entities: List[ExtractedEntityCandidate]) -> List[ExtractedEntityCandidate]:
    """
    Apply deterministic post-processing rules to clean up or filter extracted entities.
    
    Overlap Resolution Policy:
    1. If exact duplicate spans with same entity type exist, keep the first one encountered (deterministic sort applied).
    2. If overlapping spans exist, keep the one with the highest confidence.
    3. If confidence is tied, keep the longest span.
    4. If length is tied, keep the one that starts first (lowest start_offset).
    5. If start offset is tied, keep the one sorted alphabetically by entity_type.
    """
    if not entities:
        return []

    import typing
    from apps.backend.app.extraction.schemas import EntityType
    
    # 1. Filter out unsupported labels (though they should be mapped by label_mapping, we ensure it here)
    valid_labels = typing.get_args(EntityType)
    valid_entities = [e for e in entities if e.entity_type in valid_labels]

    # 2. Fix offsets to ensure text[start:end] equals original_value
    # (Assuming the original_value represents what should be at that offset, 
    # but we will just assert the offsets are strictly within text length)
    processed = []
    for e in valid_entities:
        # Check text match (if valid lengths)
        doc_text = e.source_text
        if 0 <= e.start_offset <= e.end_offset <= len(doc_text):
            span_text = doc_text[e.start_offset:e.end_offset]
            if span_text != e.original_value:
                # If they don't match, we skip or fix? The requirement: "Ensure text[start:end] equals the candidate text."
                # If it doesn't match, the extraction is malformed. We'll drop malformed ones.
                continue
        else:
            # Invalid boundaries
            continue
            
        # Ensure it has a stable candidate ID
        stable_id = generate_stable_candidate_id(
            e.source_document_id, e.start_offset, e.end_offset, e.entity_type, e.original_value
        )
        
        # We append a version tag to extraction_version if not present
        version = e.extraction_version
        if f"post_{POST_PROCESSING_VERSION}" not in version:
            version = f"{version}-post_{POST_PROCESSING_VERSION}"
            
        new_e = ExtractedEntityCandidate(
            candidate_id=stable_id,
            entity_type=e.entity_type,
            original_value=e.original_value,
            normalized_value=e.normalized_value,
            source_document_id=e.source_document_id,
            source_text=e.source_text,
            start_offset=e.start_offset,
            end_offset=e.end_offset,
            confidence=e.confidence,
            verification_status="UNREVIEWED",
            extraction_provider=e.extraction_provider,
            extraction_version=version
        )
        processed.append(new_e)

    # 3. Resolve duplicates and overlaps deterministically
    # Sort by confidence (desc), then length (desc), then start_offset (asc), then entity_type (asc)
    processed.sort(key=lambda x: (-x.confidence, -(x.end_offset - x.start_offset), x.start_offset, x.entity_type))
    
    final_entities = []
    for current in processed:
        overlap = False
        for kept in final_entities:
            # Check overlap
            if not (current.end_offset <= kept.start_offset or current.start_offset >= kept.end_offset):
                overlap = True
                break
        
        if not overlap:
            final_entities.append(current)
            
    return final_entities


def calculate_confidence(label: str, model_confidence: float | None = None) -> float:
    """Calculate a synthetic confidence score if the model does not provide one."""
    if model_confidence is not None:
        return model_confidence
    return 0.85
