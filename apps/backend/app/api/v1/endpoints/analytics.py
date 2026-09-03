"""Analytics API endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.backend.app.db.session import get_db
from apps.backend.app.analytics.schemas import AnalyticsRunResponse, EntityGraphFeatures, CaseGraphAnalytics, PatternAlert
from apps.backend.app.analytics.service import AnalyticsService
from apps.backend.app.analytics.config import analytics_settings
from apps.backend.app.models.alert import Alert
from apps.backend.app.models.analytics import EntityGraphFeature, CaseGraphAnalytics as CaseGraphAnalyticsModel
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.graph.service import GraphService


router = APIRouter()
graph_service = GraphService()


@router.get("/analytics/health", response_model=dict[str, Any])
def get_analytics_health() -> dict[str, Any]:
    """Check availability of analytics components (Neo4j and GDS)."""
    # Simple check for now
    try:
        health = graph_service.health_check()
        return {
            "status": "healthy" if health.neo4j_available else "GRAPH_UNAVAILABLE",
            "neo4j_available": health.neo4j_available,
            "engine": "networkx_fallback", # We know this is fallback driven
            "gds_available": False,
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e)
        }


@router.post("/cases/{case_id}/analytics", response_model=AnalyticsRunResponse)
def run_case_analytics(case_id: str, db: Session = Depends(get_db)) -> AnalyticsRunResponse:
    """Execute graph analytics and pattern detection on a case."""
    
    # Fetch graph
    try:
        graph_response = graph_service.get_case_subgraph(
            case_id, limit=analytics_settings.ANALYTICS_MAX_NODES
        )
    except Exception:
        # E.g. Offline
        graph_response = None
        
    service = AnalyticsService(case_id)
    response, features, alerts = service.run_analysis(graph_response)
    
    # Persist Results idempotently
    if response.status not in ("GRAPH_UNAVAILABLE", "NO_GRAPH_DATA", "FAILED"):
        # We delete old unreviewed alerts/features for this case if they don't match this run id
        # For simplicity, we just insert the new ones, though to be fully idempotent:
        
        # 1. Delete prior features for this case
        db.query(EntityGraphFeature).filter(EntityGraphFeature.case_id == case_id).delete()
        db.query(CaseGraphAnalyticsModel).filter(CaseGraphAnalyticsModel.case_id == case_id).delete()
        
        # 2. Insert case metrics
        case_metric = CaseGraphAnalyticsModel(
            case_id=case_id,
            node_count=response.node_count,
            edge_count=response.edge_count,
            community_count=0, # Simplified
            density=0.0,
            algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
            analytics_engine=response.analytics_engine.value,
            analysis_run_id=response.analysis_run_id,
            status=response.status.value,
            truncated=False,
        )
        db.add(case_metric)
        
        # 3. Insert entity features
        for f in features.values():
            ef = EntityGraphFeature(
                entity_id=f.entity_id,
                case_id=case_id,
                entity_type=f.entity_type,
                degree=f.degree,
                in_degree=f.in_degree,
                out_degree=f.out_degree,
                case_count=f.case_count,
                unique_neighbour_count=f.unique_neighbour_count,
                shared_location_count=f.shared_location_count,
                shared_phone_count=f.shared_phone_count,
                shared_vehicle_count=f.shared_vehicle_count,
                transaction_count=f.transaction_count,
                transaction_total=f.transaction_total,
                pagerank_score=f.pagerank_score,
                betweenness_score=f.betweenness_score,
                bridge_score=f.bridge_score,
                algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                analytics_engine=response.analytics_engine.value,
                analysis_run_id=response.analysis_run_id
            )
            db.add(ef)
            
        # 4. Insert alerts
        # Find existing OPEN alerts for this case to avoid duplicates if they match the same entity set
        # For MVP, we'll just clear OPEN alerts and insert new ones
        db.query(Alert).filter(
            Alert.case_id == case_id,
            Alert.status == "OPEN"
        ).delete()
        
        for a in alerts:
            db_alert = Alert(
                case_id=case_id,
                alert_type=a.pattern_type,
                title=a.title,
                description=a.explanation,
                severity=a.severity.value,
                confidence_score=a.score,
                evidence_ids=a.evidence_ids,
                feature_values=a.feature_values,
                rule_version=a.rule_version,
                analytics_engine=a.analytics_engine,
                algorithm_version=a.algorithm_version,
                analysis_run_id=a.analysis_run_id,
                requires_human_verification=a.requires_human_verification,
                status=a.status.value
            )
            db.add(db_alert)
            
        db.commit()
        
    return response


@router.get("/cases/{case_id}/patterns")
def get_case_patterns(case_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Retrieve pattern alerts for a case."""
    alerts = db.query(Alert).filter(Alert.case_id == case_id).order_by(Alert.created_at.desc()).all()
    # Map to schema-like dictionary
    return [{
        "alert_id": a.id,
        "case_id": a.case_id,
        "pattern_type": a.alert_type,
        "title": a.title,
        "explanation": a.description,
        "severity": a.severity,
        "score": float(a.confidence_score) if a.confidence_score else 0.0,
        "evidence_ids": a.evidence_ids or [],
        "feature_values": a.feature_values or {},
        "status": a.status,
        "created_at": a.created_at
    } for a in alerts]


@router.get("/cases/{case_id}/features")
def get_case_features(case_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Retrieve all entity graph features for a case."""
    features = db.query(EntityGraphFeature).filter(EntityGraphFeature.case_id == case_id).all()
    return [{
        "entity_id": f.entity_id,
        "degree": f.degree,
        "pagerank_score": f.pagerank_score,
        "betweenness_score": f.betweenness_score,
        "bridge_score": f.bridge_score
    } for f in features]


@router.post("/alerts/{alert_id}/review")
def review_alert(alert_id: str, action: str, rationale: str = "", db: Session = Depends(get_db)):
    """Human review of a pattern alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    action = action.upper()
    valid_actions = ["ACCEPT", "REJECT", "CORRECT", "NEEDS_MORE_INFORMATION"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    if action in ["CORRECT", "NEEDS_MORE_INFORMATION"] and not rationale:
        raise HTTPException(status_code=400, detail="Rationale required for this action")
        
    # Map to valid status
    if action == "ACCEPT":
        alert.status = "ACCEPTED"
    elif action == "REJECT":
        alert.status = "REJECTED"
    elif action == "CORRECT":
        alert.status = "CORRECTED"
    elif action == "NEEDS_MORE_INFORMATION":
        alert.status = "NEEDS_MORE_INFORMATION"
        
    alert.reviewed_at = datetime.now(timezone.utc)
    
    # Audit log
    audit = AuditLog(
        user_id=analytics_settings.DEV_REVIEWER_ID,
        action=f"REVIEW_ALERT_{action}",
        target_type="ALERT",
        target_id=alert_id,
        rationale=rationale
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "alert_id": alert_id, "new_status": alert.status}
