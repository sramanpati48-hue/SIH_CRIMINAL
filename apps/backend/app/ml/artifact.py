"""Secure artifact management for ML models."""
import os
import hashlib
import uuid
import joblib
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
import sklearn
import sys

from apps.backend.app.models.ml import ModelArtifact

# Note: In a real environment, this should come from a settings/config module
ARTIFACT_ROOT = os.getenv("MODEL_ARTIFACT_ROOT", "D:/Sih/apps/backend/model_artifacts")

class UnsafeArtifactPathError(Exception):
    pass

class ArtifactSecurityError(Exception):
    pass

def _get_trusted_root() -> Path:
    root = Path(ARTIFACT_ROOT).resolve()
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
    return root

def _compute_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_model_artifact(
    db: Session,
    model: any,
    model_type: str,
    model_version: str,
    dataset_version: str,
    feature_version: str,
    feature_names: list,
    training_case_ids: list,
    hyperparameters: dict,
    metrics: dict = None
) -> ModelArtifact:
    """Saves a model to the trusted root securely and registers it in the DB."""
    artifact_id = f"art_{uuid.uuid4().hex[:12]}"
    
    # Internal generation of filename and storage key (no user input)
    now = datetime.now(timezone.utc)
    date_path = now.strftime("%Y/%m/%d")
    filename = f"{model_type}_{artifact_id}.joblib"
    storage_key = f"artifacts/{date_path}/{artifact_id}/{filename}"
    
    trusted_root = _get_trusted_root()
    relative_dir = Path(f"artifacts/{date_path}/{artifact_id}")
    full_dir = (trusted_root / relative_dir).resolve()
    
    # Prevent path traversal
    if trusted_root not in full_dir.parents and trusted_root != full_dir:
        raise UnsafeArtifactPathError("Generated path escaped trusted root.")
        
    full_dir.mkdir(parents=True, exist_ok=True)
    file_path = full_dir / filename
    
    # Save the artifact using joblib
    joblib.dump(model, file_path)
    
    checksum = _compute_sha256(file_path)
    
    db_artifact = ModelArtifact(
        id=str(uuid.uuid4()),
        artifact_id=artifact_id,
        model_type=model_type,
        model_version=model_version,
        dataset_version=dataset_version,
        feature_version=feature_version,
        artifact_filename=filename,
        storage_key=storage_key,
        sha256_checksum=checksum,
        scikit_learn_version=sklearn.__version__,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        feature_names=feature_names,
        training_case_ids=training_case_ids,
        hyperparameters=hyperparameters,
        metrics=metrics or {},
        status="READY"
    )
    
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    
    return db_artifact

def load_model_artifact(db: Session, artifact_id: str):
    """Loads a model artifact securely with strict verification."""
    db_artifact = db.query(ModelArtifact).filter(ModelArtifact.artifact_id == artifact_id).first()
    if not db_artifact:
        raise ArtifactSecurityError("Artifact ID not found.")
        
    if db_artifact.status != "READY":
        raise ArtifactSecurityError(f"Artifact status is {db_artifact.status}, cannot load.")
        
    trusted_root = _get_trusted_root()
    
    # Reconstruct path from trusted components
    file_path = (trusted_root / db_artifact.storage_key).resolve()
    
    # Check boundaries
    if trusted_root not in file_path.parents and trusted_root != file_path:
        db_artifact.status = "REJECTED"
        db.commit()
        raise UnsafeArtifactPathError("Path traversal attempt detected.")
        
    if not file_path.exists():
        db_artifact.status = "MISSING"
        db.commit()
        raise ArtifactSecurityError("Artifact physical file is missing.")
        
    # Verify Checksum
    current_checksum = _compute_sha256(file_path)
    if current_checksum != db_artifact.sha256_checksum:
        db_artifact.status = "CHECKSUM_INVALID"
        db.commit()
        raise ArtifactSecurityError("Artifact checksum mismatch. File is corrupted or tampered.")
        
    # Environment version checks
    if db_artifact.scikit_learn_version != sklearn.__version__:
        # Strictly speaking, loading different scikit-learn versions can be unsafe or buggy
        db_artifact.status = "INCOMPATIBLE"
        db.commit()
        raise ArtifactSecurityError("Incompatible scikit-learn version.")
        
    # Finally, load
    try:
        model = joblib.load(file_path)
    except Exception as e:
        db_artifact.status = "REJECTED"
        db.commit()
        raise ArtifactSecurityError(f"Deserialization failed: {e}")
        
    return model
