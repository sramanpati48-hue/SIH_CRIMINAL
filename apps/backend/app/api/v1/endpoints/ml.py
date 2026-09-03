"""API Endpoints for Machine Learning Models."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
import datetime

from apps.backend.app.db.session import get_db
from apps.backend.app.models.case import Case
from apps.backend.app.models.ml import ModelPrediction
from apps.backend.app.models.alert import Alert
from apps.backend.app.ml.dataset import build_dataset
from apps.backend.app.ml.models import train_and_predict_anomaly, train_and_predict_supervised
from apps.backend.app.ml.comparison import generate_comparison

router = APIRouter()

@router.post("/{case_id}/predict")
def run_predictions(
    case_id: str,
    db: Session = Depends(get_db)
):
    """Runs baseline ML models for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        dataset = build_dataset(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Idempotency check: if predictions exist for this dataset version, reuse them
    dataset_version = dataset["dataset_version"]
    existing_preds = db.query(ModelPrediction).filter(
        ModelPrediction.case_id == case_id,
        ModelPrediction.dataset_version == dataset_version
    ).all()
    
    anomaly_pred = next((p for p in existing_preds if p.prediction_type == "anomaly"), None)
    if not anomaly_pred:
        anomaly_pred = train_and_predict_anomaly(db, dataset, case_id)
    
    priority_pred = next((p for p in existing_preds if p.prediction_type == "priority"), None)
    if not priority_pred:
        priority_pred = train_and_predict_supervised(db, dataset, case_id)
    
    # Generate Comparison
    rule_alerts = db.query(Alert).filter(Alert.case_id == case_id, Alert.status == "OPEN").all()
    similarity_results = [] # we'd fetch this if needed
    
    comparison = generate_comparison(rule_alerts, anomaly_pred, priority_pred, similarity_results)

    # Format response safely (converting SQLAlchemy objects to dicts)
    def pred_to_dict(p):
        if not p: return None
        if isinstance(p, dict): return p
        return {
            "prediction_type": p.prediction_type,
            "prediction": p.prediction,
            "score": p.score,
            "explanation": p.explanation,
            "top_features": p.top_features,
            "model_version": p.model_version,
            "dataset_version": p.dataset_version,
            "feature_version": p.feature_version,
            "requires_human_verification": p.requires_human_verification,
            "created_at": p.created_at.isoformat()
        }

    return {
        "case_id": case_id,
        "dataset_metadata": {
            "dataset_version": dataset["dataset_version"],
            "feature_version": dataset["feature_version"],
            "supervised_valid": dataset["supervised_valid"],
            "supervised_reason": dataset["supervised_reason"],
            "total_cases": len(dataset["case_ids"]),
            "class_distribution": dataset.get("class_distribution", {})
        },
        "anomaly_baseline": pred_to_dict(anomaly_pred),
        "supervised_baseline": pred_to_dict(priority_pred),
        "comparison": comparison,
        "warnings": ["Synthetic data warning: Models trained on synthetic data do not represent real-world accuracy.",
                     "Human verification warning: Predictions are for investigative prioritization only."]
    }

@router.get("/{case_id}/predictions")
def get_predictions(
    case_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves existing predictions for a case."""
    preds = db.query(ModelPrediction).filter(ModelPrediction.case_id == case_id).order_by(ModelPrediction.created_at.desc()).all()
    
    results = []
    for p in preds:
        results.append({
            "id": p.id,
            "prediction_type": p.prediction_type,
            "prediction": p.prediction,
            "score": p.score,
            "explanation": p.explanation,
            "top_features": p.top_features,
            "model_version": p.model_version,
            "dataset_version": p.dataset_version,
            "feature_version": p.feature_version,
            "requires_human_verification": p.requires_human_verification,
            "created_at": p.created_at
        })
        
    return results

@router.get("/{case_id}/model-metadata")
def get_model_metadata(
    case_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves metadata about the models used for this case."""
    preds = db.query(ModelPrediction).filter(ModelPrediction.case_id == case_id).order_by(ModelPrediction.created_at.desc()).all()
    if not preds:
        return {"message": "No models ran for this case yet."}
        
    p = preds[0]
    return {
        "model_version": p.model_version,
        "dataset_version": p.dataset_version,
        "feature_version": p.feature_version,
        "library": "scikit-learn",
        "timestamp": p.created_at
    }

@router.get("/health")
def ml_health():
    """Health check for ML module."""
    import sklearn
    return {
        "status": "healthy",
        "scikit_learn_version": sklearn.__version__,
        "limitations": "Synthetic data only. Baseline models active."
    }
