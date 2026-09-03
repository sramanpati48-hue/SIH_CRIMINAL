import pytest
from apps.backend.app.ml.dataset import build_dataset, MIN_SUPERVISED_CASES, InsufficientDataError
from apps.backend.app.models.ml import CaseFeatureVector
import uuid

def test_build_dataset_insufficient_cases(db_session):
    """Verify MIN_SUPERVISED_CASES enforcement."""
    # Create 19 cases (1 short of the 20 minimum)
    for _ in range(MIN_SUPERVISED_CASES - 1):
        vec = CaseFeatureVector(
            id=str(uuid.uuid4()),
            case_id=str(uuid.uuid4()),
            feature_names=["f1"],
            feature_values=[1.0],
            feature_version="v1",
            analysis_run_id="run1"
        )
        db_session.add(vec)
    db_session.commit()
    
    dataset = build_dataset(db_session)
    assert dataset["supervised_valid"] is False
    assert "below MIN_SUPERVISED_CASES" in dataset["supervised_reason"]

def test_build_dataset_empty(db_session):
    """Test exception on totally empty database."""
    with pytest.raises(InsufficientDataError):
        build_dataset(db_session)

def test_build_dataset_single_class(db_session):
    """Verify fallback if all labels are the same class."""
    for _ in range(MIN_SUPERVISED_CASES + 5):
        vec = CaseFeatureVector(
            id=str(uuid.uuid4()),
            case_id=str(uuid.uuid4()),
            feature_names=["f1"],
            feature_values=[1.0],
            feature_version="v1",
            analysis_run_id="run1"
        )
        db_session.add(vec)
    db_session.commit()
    
    # Since we have no Alerts in DB, all will be class 0 (no priority)
    dataset = build_dataset(db_session)
    
    assert dataset["supervised_valid"] is False
    assert "two classes exist" in dataset["supervised_reason"]
