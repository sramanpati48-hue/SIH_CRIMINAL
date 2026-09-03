import pytest
from apps.backend.app.api.v1.endpoints.ml import run_predictions
from apps.backend.app.models.ml import ModelPrediction, CaseFeatureVector
from apps.backend.app.models.case import Case
from apps.backend.app.ml.dataset import MIN_SUPERVISED_CASES
import uuid

def test_ml_api_insufficient_data(db_session):
    """Test ml API gracefully rejects RF training on insufficient data without crashing."""
    
    case_id = str(uuid.uuid4())
    c0 = Case(id=case_id, case_number="T0", title="T0", status="OPEN", priority="LOW")
    db_session.add(c0)
    db_session.commit()
    
    vec = CaseFeatureVector(
        id=str(uuid.uuid4()),
        case_id=case_id,
        feature_names=["f1"],
        feature_values=[1.0],
        feature_version="v1",
        analysis_run_id="run1"
    )
    db_session.add(vec)
    db_session.commit()
    
    res = run_predictions(case_id, db_session)
    
    # Isolation forest should work
    assert res["anomaly_baseline"] is not None
    # Supervised should be INSUFFICIENT_DATA
    assert res["supervised_baseline"]["status"] == "INSUFFICIENT_DATA"
    
    assert res["dataset_metadata"]["supervised_valid"] is False
    assert "below MIN_SUPERVISED_CASES" in res["dataset_metadata"]["supervised_reason"]
    
    # Ensure no ModelPrediction for priority was created
    priority_count = db_session.query(ModelPrediction).filter(
        ModelPrediction.case_id == case_id, 
        ModelPrediction.prediction_type == "priority"
    ).count()
    assert priority_count == 0
