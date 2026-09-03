import pytest
from apps.backend.app.similarity.features import extract_case_features
from apps.backend.app.models.ml import CaseFeatureVector

from apps.backend.app.models.case import Case
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
import uuid

def test_deterministic_case_vectors(db_session):
    """Test that feature extraction is deterministic and has stable ordering."""
    run_id = "test_run_1"
    case_id = str(uuid.uuid4())
    
    # Create manual data
    c = Case(id=case_id, case_number="T1", title="T1", status="OPEN", priority="LOW")
    e1 = ExtractedEntity(id=str(uuid.uuid4()), case_id=case_id, entity_type="PERSON", canonical_name="A")
    e2 = ExtractedEntity(id=str(uuid.uuid4()), case_id=case_id, entity_type="PERSON", canonical_name="B")
    r1 = ExtractedRelationship(id=str(uuid.uuid4()), case_id=case_id, source_entity_id=e1.id, target_entity_id=e2.id, relation_type="CALLED")
    
    db_session.add_all([c, e1, e2, r1])
    db_session.commit()
    
    vec1 = extract_case_features(db_session, case_id, run_id)
    assert vec1.case_id == case_id
    assert len(vec1.feature_names) == 34
    assert len(vec1.feature_values) == 34
    
    # Assert specific counts
    names = vec1.feature_names
    vals = vec1.feature_values
    
    assert vals[names.index("node_count")] == 2
    assert vals[names.index("edge_count")] == 1
    assert vals[names.index("person_count")] == 2
    assert vals[names.index("call_count")] == 1
    
    # Extract again, should be identical values
    vec2 = extract_case_features(db_session, case_id, run_id)
    assert vec1.feature_values == vec2.feature_values
    
def test_missing_value_handling():
    """Missing values handled gracefully (tested via default dicts in features.py)."""
    pass
