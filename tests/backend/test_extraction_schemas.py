import pytest
from apps.backend.app.extraction.schemas import ExtractedEntityCandidate, ExtractedRelationshipCandidate

def test_entity_schema_valid():
    ent = ExtractedEntityCandidate(
        candidate_id="c1",
        entity_type="PERSON",
        original_value="John Doe",
        normalized_value="John Doe",
        source_document_id="d1",
        source_text="John Doe",
        start_offset=0,
        end_offset=8,
        confidence=0.9,
        extraction_provider="test",
        extraction_version="1.0"
    )
    assert ent.confidence == 0.9

def test_entity_schema_invalid_confidence():
    with pytest.raises(ValueError):
        ExtractedEntityCandidate(
            candidate_id="c1",
            entity_type="PERSON",
            original_value="John Doe",
            normalized_value="John Doe",
            source_document_id="d1",
            source_text="John Doe",
            start_offset=0,
            end_offset=8,
            confidence=1.5,
            extraction_provider="test",
            extraction_version="1.0"
        )

def test_entity_schema_invalid_offsets():
    with pytest.raises(ValueError):
        ExtractedEntityCandidate(
            candidate_id="c1",
            entity_type="PERSON",
            original_value="John Doe",
            normalized_value="John Doe",
            source_document_id="d1",
            source_text="John Doe",
            start_offset=10,
            end_offset=8, # Invalid, end < start
            confidence=0.9,
            extraction_provider="test",
            extraction_version="1.0"
        )

def test_entity_schema_invalid_type():
    with pytest.raises(ValueError):
        ExtractedEntityCandidate(
            candidate_id="c1",
            entity_type="DOG", # Not in allow list
            original_value="Fido",
            normalized_value="Fido",
            source_document_id="d1",
            source_text="Fido",
            start_offset=0,
            end_offset=4,
            confidence=0.9,
            extraction_provider="test",
            extraction_version="1.0"
        )
