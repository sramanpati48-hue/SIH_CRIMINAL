import pytest
import os
import uuid
import hashlib
import sklearn
from pathlib import Path
from sklearn.ensemble import IsolationForest
import numpy as np

from apps.backend.app.ml.artifact import (
    save_model_artifact,
    load_model_artifact,
    UnsafeArtifactPathError,
    ArtifactSecurityError,
    _get_trusted_root,
    ARTIFACT_ROOT
)
from apps.backend.app.models.ml import ModelArtifact

@pytest.fixture
def dummy_model():
    model = IsolationForest(n_estimators=5, random_state=42)
    X = np.random.rand(10, 5)
    model.fit(X)
    return model

def test_save_model_artifact_trusted(db_session, dummy_model):
    """Test standard valid artifact saving."""
    artifact = save_model_artifact(
        db=db_session,
        model=dummy_model,
        model_type="TestModel",
        model_version="v1",
        dataset_version="d1",
        feature_version="f1",
        feature_names=["a", "b"],
        training_case_ids=["case1"],
        hyperparameters={"test": True}
    )
    
    assert artifact.artifact_id.startswith("art_")
    assert artifact.status == "READY"
    assert artifact.sha256_checksum
    
    # Path should exist
    full_path = (_get_trusted_root() / artifact.storage_key).resolve()
    assert full_path.exists()
    
    loaded_model = load_model_artifact(db_session, artifact.artifact_id)
    assert loaded_model is not None

def test_load_missing_artifact(db_session, dummy_model):
    """Test loading when physical file is deleted."""
    artifact = save_model_artifact(
        db=db_session,
        model=dummy_model,
        model_type="TestModel",
        model_version="v1",
        dataset_version="d1",
        feature_version="f1",
        feature_names=[],
        training_case_ids=[],
        hyperparameters={}
    )
    
    full_path = (_get_trusted_root() / artifact.storage_key).resolve()
    full_path.unlink() # Delete it
    
    with pytest.raises(ArtifactSecurityError, match="missing"):
        load_model_artifact(db_session, artifact.artifact_id)
        
    db_session.refresh(artifact)
    assert artifact.status == "MISSING"

def test_load_corrupted_checksum(db_session, dummy_model):
    """Test checksum validation."""
    artifact = save_model_artifact(
        db=db_session,
        model=dummy_model,
        model_type="TestModel",
        model_version="v1",
        dataset_version="d1",
        feature_version="f1",
        feature_names=[],
        training_case_ids=[],
        hyperparameters={}
    )
    
    # Corrupt the file
    full_path = (_get_trusted_root() / artifact.storage_key).resolve()
    with open(full_path, "ab") as f:
        f.write(b"tampered")
        
    with pytest.raises(ArtifactSecurityError, match="mismatch"):
        load_model_artifact(db_session, artifact.artifact_id)
        
    db_session.refresh(artifact)
    assert artifact.status == "CHECKSUM_INVALID"

def test_load_invalid_id(db_session):
    """Test invalid artifact ID."""
    with pytest.raises(ArtifactSecurityError, match="not found"):
        load_model_artifact(db_session, "nonexistent")

def test_path_traversal_prevention(db_session, dummy_model, monkeypatch):
    """Test path traversal is caught."""
    artifact = save_model_artifact(
        db=db_session,
        model=dummy_model,
        model_type="TestModel",
        model_version="v1",
        dataset_version="d1",
        feature_version="f1",
        feature_names=[],
        training_case_ids=[],
        hyperparameters={}
    )
    
    # Manually inject traversal attempt into the DB storage key
    artifact.storage_key = "../../../Windows/System32/cmd.exe"
    db_session.commit()
    
    with pytest.raises(UnsafeArtifactPathError, match="traversal"):
        load_model_artifact(db_session, artifact.artifact_id)
