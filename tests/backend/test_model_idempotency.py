import pytest
from apps.backend.app.api.v1.endpoints.ml import run_predictions
from apps.backend.app.models.ml import ModelPrediction, CaseFeatureVector
from apps.backend.app.models.case import Case
import uuid

def test_run_predictions_idempotent(db_session):
    """Test that predicting twice on same dataset yields the same records without duplication."""
    
    # We need a case in the DB
    case_id = str(uuid.uuid4())
    c0 = Case(id=case_id, case_number="T0", title="T0", status="OPEN", priority="LOW")
    db_session.add(c0)
    db_session.commit()
    
    # We need some CaseFeatureVectors so dataset can build
    for i in range(25): # satisfy supervised
        cid = case_id if i == 0 else str(uuid.uuid4())
        # Case has to exist for case_id
        if i > 0:
            c = Case(id=cid, case_number=f"T{i}", title=f"T{i}", status="OPEN", priority="LOW")
            db_session.add(c)
        vec = CaseFeatureVector(
            id=str(uuid.uuid4()),
            case_id=cid,
            feature_names=["f1"],
            feature_values=[1.0],
            feature_version="v1",
            analysis_run_id="run1"
        )
        db_session.add(vec)
        
        # Add an alert to some cases to create 2 classes for supervised learning
        from apps.backend.app.models.alert import Alert
        if i % 2 == 0:
            a = Alert(id=str(uuid.uuid4()), case_id=cid, alert_type="FINANCIAL_LOOP", title="Test", severity="HIGH", status="OPEN", description="T")
            db_session.add(a)
            
    db_session.commit()
    
    # Run first time
    res1 = run_predictions(case_id, db_session)
    
    anomaly1 = res1["anomaly_baseline"]
    supervised1 = res1["supervised_baseline"]
    
    assert anomaly1 is not None
    assert supervised1 is not None
    
    # Check DB count
    count1 = db_session.query(ModelPrediction).filter(ModelPrediction.case_id == case_id).count()
    assert count1 == 2
    
    # Run second time
    res2 = run_predictions(case_id, db_session)
    
    # Check DB count (should not duplicate)
    count2 = db_session.query(ModelPrediction).filter(ModelPrediction.case_id == case_id).count()
    assert count2 == 2
    
    assert res2["anomaly_baseline"]["model_version"] == anomaly1["model_version"]
