"""ML Baseline Models (Isolation Forest, Random Forest)."""
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from apps.backend.app.models.ml import ModelPrediction
from .versioning import generate_model_version
from .artifact import save_model_artifact

def normalize_to_zero_one(values: np.ndarray) -> np.ndarray:
    """Normalizes an array of values to the [0, 1] range."""
    min_val = np.min(values)
    max_val = np.max(values)
    if max_val == min_val:
        return np.zeros_like(values)
    return (values - min_val) / (max_val - min_val)

def train_and_predict_anomaly(db: Session, dataset: dict, target_case_id: str):
    """Trains Isolation Forest on the dataset and returns prediction for target_case_id."""
    case_ids = dataset["case_ids"]
    X = dataset["X_full"]
    feature_names = dataset["feature_names"]
    
    # Verify target exists
    if target_case_id not in case_ids:
        return None
        
    target_idx = case_ids.index(target_case_id)
    target_vec = X[target_idx].reshape(1, -1)
    
    # Train Isolation Forest (Anomaly detection)
    model = IsolationForest(
        random_state=42, 
        contamination=0.1, 
        n_estimators=100
    )
    model.fit(X)
    
    # Score direction: sklearn Isolation Forest decision_function returns lower values for more anomalous cases.
    # We explicitly invert and normalize it so higher score = more anomalous.
    raw_decision = model.decision_function(X)
    anomaly_value = -raw_decision
    anomaly_scores = normalize_to_zero_one(anomaly_value)
    
    target_score = float(anomaly_scores[target_idx])
    
    # Rank (1 = most anomalous)
    rank = int((np.argsort(-anomaly_scores) == target_idx).nonzero()[0][0]) + 1
    
    # Save Artifact
    model_version = generate_model_version(dataset["dataset_version"], "IsolationForest", {"contamination": 0.1, "score_transformation_version": "1"})
    
    db_artifact = save_model_artifact(
        db=db,
        model=model,
        model_type="IsolationForest",
        model_version=model_version,
        dataset_version=dataset["dataset_version"],
        feature_version=dataset["feature_version"],
        feature_names=feature_names,
        training_case_ids=case_ids,
        hyperparameters={"contamination": 0.1, "n_estimators": 100},
        metrics={"score_transformation_version": "1"}
    )
    
    # Explain unusual features (simple absolute deviation from mean)
    means = np.mean(X, axis=0)
    stds = np.std(X, axis=0) + 1e-6 # prevent div/0
    
    z_scores = (target_vec[0] - means) / stds
    abs_z = np.abs(z_scores)
    
    top_indices = np.argsort(abs_z)[-3:][::-1] # top 3 most unusual features
    unusual_features = []
    explanation_parts = []
    
    top_feature_dict = {}
    
    for idx in top_indices:
        feat_name = feature_names[idx]
        val = float(target_vec[0][idx])
        mean_val = float(means[idx])
        z = z_scores[idx]
        direction = "higher" if z > 0 else "lower"
        
        if abs_z[idx] > 1.0: # Only report if it's actually somewhat unusual
            unusual_features.append(feat_name)
            explanation_parts.append(f"{feat_name} ({val:.2f}) is {direction} than the baseline ({mean_val:.2f})")
            top_feature_dict[feat_name] = {
                "observed_value": val,
                "baseline_value": mean_val,
                "direction": direction,
                "explanation": f"Unusual compared with baseline ({direction})",
                "related_alerts": [],
                "evidence_ids": []
            }
            
    if explanation_parts:
        explanation = "Compared with the configured synthetic baseline, this case is unusual because " + " and ".join(explanation_parts) + "."
    else:
        explanation = "This case does not exhibit significant structural deviations from the synthetic baseline."
        
    model_version = generate_model_version(dataset["dataset_version"], "IsolationForest", {"contamination": 0.1})
    run_id = str(uuid.uuid4())
    
    pred = ModelPrediction(
        id=str(uuid.uuid4()),
        case_id=target_case_id,
        prediction_type="anomaly",
        prediction="ANOMALOUS" if target_score > 0 else "NORMAL",
        score=target_score,
        explanation=explanation,
        top_features=top_feature_dict,
        model_version=model_version,
        dataset_version=dataset["dataset_version"],
        feature_version=dataset["feature_version"],
        analysis_run_id=run_id
    )
    
    db.add(pred)
    db.commit()
    
    return pred

def train_and_predict_supervised(db: Session, dataset: dict, target_case_id: str):
    """Trains Random Forest on the dataset and returns prediction for target_case_id."""
    
    if not dataset["supervised_valid"]:
        return {
            "status": "INSUFFICIENT_DATA",
            "reason": dataset["supervised_reason"]
        }
        
    case_ids = dataset["case_ids"]
    if target_case_id not in case_ids:
        return None
        
    X_train, y_train = dataset["X_train"], dataset["y_train"]
    X_test, y_test = dataset["X_test"], dataset["y_test"]
    X_full = dataset["X_full"]
    target_idx = case_ids.index(target_case_id)
    target_vec = X_full[target_idx].reshape(1, -1)
    feature_names = dataset["feature_names"]
    
    model = RandomForestClassifier(random_state=42, n_estimators=100, class_weight='balanced')
    model.fit(X_train, y_train)
    
    # Predict target
    prob = model.predict_proba(target_vec)[0]
    pred_class = model.predict(target_vec)[0]
    score = float(prob[1])
    priority = "HIGH" if score > 0.7 else ("MEDIUM" if score > 0.4 else "LOW")
    
    # Feature importances (global, we map it to local values for context)
    importances = model.feature_importances_
    top_indices = np.argsort(importances)[-3:][::-1]
    
    top_feature_dict = {}
    explanation_parts = []
    
    # Calculate means of the training set to serve as the baseline
    means = np.mean(X_train, axis=0)
    
    for idx in top_indices:
        feat_name = feature_names[idx]
        val = float(target_vec[0][idx])
        mean_val = float(means[idx])
        direction = "contributes to investigative priority"
        
        top_feature_dict[feat_name] = {
            "observed_value": val,
            "baseline_value": mean_val,
            "direction": direction,
            "explanation": "Global model feature importance suggestion",
            "related_alerts": [],
            "evidence_ids": []
        }
        explanation_parts.append(f"{feat_name} ({val:.2f})")
        
    explanation = f"Investigative priority suggested as {priority}. Key contributing structural features (Global Importance): " + ", ".join(explanation_parts) + "."
    
    model_version = generate_model_version(dataset["dataset_version"], "RandomForest", {"n_estimators": 100, "class_weight": "balanced"})
    
    db_artifact = save_model_artifact(
        db=db,
        model=model,
        model_type="RandomForest",
        model_version=model_version,
        dataset_version=dataset["dataset_version"],
        feature_version=dataset["feature_version"],
        feature_names=feature_names,
        training_case_ids=dataset["case_train"],
        hyperparameters={"n_estimators": 100, "class_weight": "balanced"},
        metrics={"score_transformation_version": "1", "class_distribution": dataset["class_distribution"]}
    )
    
    run_id = str(uuid.uuid4())
    
    pred = ModelPrediction(
        id=str(uuid.uuid4()),
        case_id=target_case_id,
        prediction_type="priority",
        prediction=priority,
        score=score,
        explanation=explanation,
        top_features=top_feature_dict,
        model_version=model_version,
        dataset_version=dataset["dataset_version"],
        feature_version=dataset["feature_version"],
        analysis_run_id=run_id
    )
    
    db.add(pred)
    db.commit()
    
    return pred
