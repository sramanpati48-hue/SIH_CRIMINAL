"""Versioning utilities for ML artifacts."""
import hashlib
from datetime import datetime

def generate_dataset_version(case_ids: list[str], feature_version: str) -> str:
    """Generates a deterministic dataset version based on features and case inclusion."""
    sorted_cases = sorted(case_ids)
    base_string = f"{feature_version}:{','.join(sorted_cases)}"
    return f"ds-{hashlib.sha256(base_string.encode()).hexdigest()[:8]}"

def generate_model_version(dataset_version: str, algorithm: str, params: dict) -> str:
    """Generates a deterministic model version."""
    param_string = str(sorted(params.items()))
    base_string = f"{dataset_version}:{algorithm}:{param_string}"
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"m-{algorithm}-{timestamp}-{hashlib.sha256(base_string.encode()).hexdigest()[:8]}"
