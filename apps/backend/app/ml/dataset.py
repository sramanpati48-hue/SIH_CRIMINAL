"""ML Dataset generation and splitting."""
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
import numpy as np

from apps.backend.app.models.ml import CaseFeatureVector
from apps.backend.app.models.alert import Alert
from .versioning import generate_dataset_version

MIN_SUPERVISED_CASES = 20

class InsufficientDataError(Exception):
    pass

def build_dataset(db: Session):
    """
    Builds the dataset from CaseFeatureVectors.
    Extracts features (X) and determines priority class (y) based on historical alerts.
    """
    vectors = db.query(CaseFeatureVector).all()
    if not vectors:
        raise InsufficientDataError("No case feature vectors found.")
        
    case_ids = []
    X = []
    y = []
    
    # We will use whether a case has HIGH/CRITICAL alerts as a simple binary priority label
    for vec in vectors:
        case_ids.append(vec.case_id)
        X.append(vec.feature_values)
        
        # Synthetic label generation for baseline supervised
        high_severity_alerts = db.query(Alert).filter(
            Alert.case_id == vec.case_id,
            Alert.severity.in_(["HIGH", "CRITICAL"])
        ).count()
        
        y.append(1 if high_severity_alerts > 0 else 0)

    X = np.array(X)
    X = np.nan_to_num(X, nan=0.0)
    y = np.array(y)
    
    # Check minimum requirements for supervised learning
    if len(case_ids) < MIN_SUPERVISED_CASES:
        supervised_valid = False
        supervised_reason = f"Labelled case count ({len(case_ids)}) is below MIN_SUPERVISED_CASES ({MIN_SUPERVISED_CASES})."
    elif len(np.unique(y)) < 2:
        supervised_valid = False
        supervised_reason = "Less than two classes exist in the target labels."
    else:
        supervised_valid = True
        supervised_reason = "Valid"
        
    feature_version = vectors[0].feature_version if vectors else "unknown"
    dataset_version = generate_dataset_version(case_ids, feature_version)
    
    # Stratified split at the case level
    if supervised_valid:
        try:
            indices = np.arange(len(case_ids))
            train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42, stratify=y)
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            case_train = [case_ids[i] for i in train_idx]
            case_test = [case_ids[i] for i in test_idx]
        except ValueError as e:
            # Fails if class distribution is too skewed
            supervised_valid = False
            supervised_reason = f"Train/test splitting failed: {str(e)}"
            X_train, X_test, y_train, y_test = None, None, None, None
            case_train, case_test = [], []
    else:
        X_train, X_test, y_train, y_test = None, None, None, None
        case_train, case_test = [], []

    return {
        "case_ids": case_ids,
        "X_full": X,
        "y_full": y,
        "feature_names": vectors[0].feature_names if vectors else [],
        "dataset_version": dataset_version,
        "feature_version": feature_version,
        "supervised_valid": supervised_valid,
        "supervised_reason": supervised_reason,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "case_train": case_train,
        "case_test": case_test,
        "class_distribution": {
            "0 (Low Priority)": int(np.sum(y == 0)),
            "1 (High Priority)": int(np.sum(y == 1))
        }
    }
