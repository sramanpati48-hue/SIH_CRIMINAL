import pytest
import numpy as np
from apps.backend.app.ml.models import normalize_to_zero_one, train_and_predict_anomaly, train_and_predict_supervised
from apps.backend.app.models.ml import ModelPrediction
import uuid

def test_normalize_to_zero_one():
    """Test score transformation boundaries."""
    arr = np.array([-0.5, 0.0, 0.5])
    normalized = normalize_to_zero_one(arr)
    assert np.min(normalized) == 0.0
    assert np.max(normalized) == 1.0
    assert normalized[1] == 0.5
    
    # Test flat array
    flat = np.array([0.5, 0.5, 0.5])
    norm_flat = normalize_to_zero_one(flat)
    assert np.all(norm_flat == 0.0)

def test_anomaly_score_direction(db_session):
    """Verify Isolation Forest higher score = more unusual."""
    
    # Create an obvious anomaly
    case_ids = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c_anomaly"]
    
    # 10 identical baseline cases (features = 1)
    X = np.ones((10, 5))
    
    # 1 highly unusual case (features = 100)
    anomaly_vec = np.ones((1, 5)) * 100
    X_full = np.vstack([X, anomaly_vec])
    
    dataset = {
        "case_ids": case_ids,
        "X_full": X_full,
        "feature_names": ["f1", "f2", "f3", "f4", "f5"],
        "dataset_version": "test",
        "feature_version": "test"
    }
    
    pred_normal = train_and_predict_anomaly(db_session, dataset, "c1")
    pred_anomaly = train_and_predict_anomaly(db_session, dataset, "c_anomaly")
    
    # Prove higher score means more unusual
    assert pred_anomaly.score > pred_normal.score
    assert pred_anomaly.prediction == "ANOMALOUS"
    
    # Verify terminology in explanation
    top_f = list(pred_anomaly.top_features.keys())[0]
    assert "Unusual compared with baseline" in pred_anomaly.top_features[top_f]["explanation"]
    assert "higher" in pred_anomaly.top_features[top_f]["direction"]
    assert "probability" not in pred_anomaly.explanation.lower()

def test_anomaly_missing_case(db_session):
    """Test safe handling when requested case isn't in dataset."""
    dataset = {
        "case_ids": ["c1"],
        "X_full": np.ones((1, 5)),
        "feature_names": [],
        "dataset_version": "test",
        "feature_version": "test"
    }
    pred = train_and_predict_anomaly(db_session, dataset, "c2")
    assert pred is None
