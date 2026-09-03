import pytest
import uuid
from apps.backend.app.similarity.service import calculate_historical_similarity
from apps.backend.app.models.ml import CaseFeatureVector

from apps.backend.app.models.case import Case
import uuid
import math

def test_calculate_similarity_no_data(db_session):
    """Test similarity with no data."""
    case_id = str(uuid.uuid4())
    c = Case(id=case_id, case_number="T1", title="T1", status="OPEN", priority="LOW")
    db_session.add(c)
    db_session.commit()
    
    res = calculate_historical_similarity(db_session, case_id)
    assert res == []

def test_similarity_ordering_and_tie_breaking(db_session):
    """Test similarity sorting and deterministic tie-breaking."""
    case_id = str(uuid.uuid4())
    c = Case(id=case_id, case_number="T1", title="T1", status="OPEN", priority="LOW")
    
    c_aaa = Case(id="C_AAA", case_number="C_AAA", title="C_AAA", status="OPEN", priority="LOW")
    c_bbb = Case(id="C_BBB", case_number="C_BBB", title="C_BBB", status="OPEN", priority="LOW")
    c_ccc = Case(id="C_CCC", case_number="C_CCC", title="C_CCC", status="OPEN", priority="LOW")
    db_session.add_all([c, c_aaa, c_bbb, c_ccc])
    db_session.commit()
    
    # Create mock feature vectors
    features = ["node_count", "edge_count"]
    
    # Target
    vec_target = CaseFeatureVector(id=str(uuid.uuid4()), case_id=case_id, feature_names=features, feature_values=[10, 5], feature_version="1", analysis_run_id="run1")
    
    # Identical
    vec_identical1 = CaseFeatureVector(id=str(uuid.uuid4()), case_id="C_AAA", feature_names=features, feature_values=[10, 5], feature_version="1", analysis_run_id="run1")
    vec_identical2 = CaseFeatureVector(id=str(uuid.uuid4()), case_id="C_BBB", feature_names=features, feature_values=[10, 5], feature_version="1", analysis_run_id="run1")
    
    # Different
    vec_diff = CaseFeatureVector(id=str(uuid.uuid4()), case_id="C_CCC", feature_names=features, feature_values=[100, 50], feature_version="1", analysis_run_id="run1")
    
    db_session.add_all([vec_target, vec_identical1, vec_identical2, vec_diff])
    db_session.commit()
    
    res = calculate_historical_similarity(db_session, case_id)
    assert len(res) == 3
    
    # Identical should have score ~1.0
    assert res[0].similarity_score > 0.99
    assert res[1].similarity_score > 0.99
    
    # Tie breaking by case_id ascending (C_AAA before C_BBB)
    assert res[0].similar_case_id == "C_AAA"
    assert res[1].similar_case_id == "C_BBB"
    
    # Diff should be last
    assert res[2].similar_case_id == "C_CCC"
    
    # Check explanations
    assert "structural similarity" in res[0].explanation

def test_similarity_zero_vector(db_session):
    """Test handling of completely zero feature vectors to prevent NaN or errors."""
    case_id1 = str(uuid.uuid4())
    case_id2 = str(uuid.uuid4())
    c1 = Case(id=case_id1, case_number="T1", title="T1", status="OPEN", priority="LOW")
    c2 = Case(id=case_id2, case_number="T2", title="T2", status="OPEN", priority="LOW")
    db_session.add_all([c1, c2])
    db_session.commit()
    
    vec1 = CaseFeatureVector(id=str(uuid.uuid4()), case_id=case_id1, feature_names=["f1"], feature_values=[0.0], feature_version="1", analysis_run_id="r")
    vec2 = CaseFeatureVector(id=str(uuid.uuid4()), case_id=case_id2, feature_names=["f1"], feature_values=[0.0], feature_version="1", analysis_run_id="r")
    
    db_session.add_all([vec1, vec2])
    db_session.commit()
    
    res = calculate_historical_similarity(db_session, case_id1)
    assert len(res) == 1
    assert not math.isnan(res[0].similarity_score)

def test_similarity_orthogonal_vector(db_session):
    """Test orthogonal vectors score exactly 0.0."""
    case_id1 = str(uuid.uuid4())
    case_id2 = str(uuid.uuid4())
    c1 = Case(id=case_id1, case_number="T1", title="T1", status="OPEN", priority="LOW")
    c2 = Case(id=case_id2, case_number="T2", title="T2", status="OPEN", priority="LOW")
    db_session.add_all([c1, c2])
    db_session.commit()
    
    # Orthogonal vectors: [1, 0] vs [0, 1]
    vec1 = CaseFeatureVector(id=str(uuid.uuid4()), case_id=case_id1, feature_names=["f1", "f2"], feature_values=[1.0, 0.0], feature_version="1", analysis_run_id="r")
    vec2 = CaseFeatureVector(id=str(uuid.uuid4()), case_id=case_id2, feature_names=["f1", "f2"], feature_values=[0.0, 1.0], feature_version="1", analysis_run_id="r")
    
    db_session.add_all([vec1, vec2])
    db_session.commit()
    
    res = calculate_historical_similarity(db_session, case_id1)
    assert len(res) == 1
    assert abs(res[0].similarity_score) < 1e-5
