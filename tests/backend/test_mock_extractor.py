import pytest
from apps.backend.app.extraction.mock_provider import MockExtractor

def test_mock_extractor_deterministic():
    extractor = MockExtractor()
    doc_text = "John Doe called (555) 123-4567 on 2023-10-01."
    
    res1 = extractor.extract("doc1", doc_text)
    res2 = extractor.extract("doc1", doc_text)
    
    assert len(res1.entities) == len(res2.entities)
    assert res1.entities[0].candidate_id == res2.entities[0].candidate_id
    assert res1.entities[0].start_offset == res2.entities[0].start_offset
    
    assert res1.provider == "MOCK_EXTRACTOR"

def test_mock_extractor_identifies_types():
    extractor = MockExtractor()
    doc_text = "John Doe called (555) 123-4567 on 2023-10-01."
    res = extractor.extract("doc1", doc_text)
    
    types = [e.entity_type for e in res.entities]
    assert "PERSON" in types
    assert "PHONE" in types
    assert "DATE" in types
    
    assert len(res.relationships) == 1
    rel = res.relationships[0]
    assert rel.relationship_type == "CALLED"
    assert rel.source_candidate_id.startswith("ent_person")
    assert rel.target_candidate_id.startswith("ent_phone")
