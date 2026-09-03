"""Feature extraction for case similarity and ML."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import json
import uuid

from apps.backend.app.models import Case, ExtractedEntity, ExtractedRelationship, Alert, CaseGraphAnalytics, EntityGraphFeature
from apps.backend.app.models.ml import CaseFeatureVector

FEATURE_VERSION = "1.0.0"

FEATURE_NAMES = [
    # Graph structure
    "node_count", "edge_count", "graph_density", "connected_component_count",
    "community_count", "largest_community_size", "average_degree", "maximum_degree",
    "average_betweenness", "maximum_betweenness", "bridge_candidate_count",
    # Entity counts
    "person_count", "phone_count", "vehicle_count", "location_count",
    "organization_count", "bank_account_count", "event_count",
    # Relationship counts
    "call_count", "transaction_count", "location_visit_count",
    "shared_phone_count", "shared_vehicle_count", "cross_case_relationship_count",
    # Temporal features
    "event_span_hours", "average_event_gap_hours",
    "rapid_transaction_chain_count", "repeated_location_window_count",
    # Pattern features
    "cross_case_connector_count", "shared_phone_pattern_count",
    "shared_vehicle_pattern_count", "repeated_location_pattern_count",
    "bridge_pattern_count", "high_connectivity_pattern_count"
]

def extract_case_features(db: Session, case_id: str, analysis_run_id: str) -> CaseFeatureVector:
    """Deterministically extracts feature vector for a case."""
    
    # 1. Base entities
    entities = db.query(ExtractedEntity).filter(ExtractedEntity.case_id == case_id).all()
    entity_counts = {
        "person_count": 0, "phone_count": 0, "vehicle_count": 0, "location_count": 0,
        "organization_count": 0, "bank_account_count": 0, "event_count": 0
    }
    for e in entities:
        t = e.entity_type.lower()
        key = f"{t}_count"
        if key in entity_counts:
            entity_counts[key] += 1

    # 2. Relationships
    rels = db.query(ExtractedRelationship).join(
        ExtractedEntity, ExtractedRelationship.source_entity_id == ExtractedEntity.id
    ).filter(ExtractedEntity.case_id == case_id).all()
    
    rel_counts = {
        "call_count": 0, "transaction_count": 0, "location_visit_count": 0,
        "shared_phone_count": 0, "shared_vehicle_count": 0, "cross_case_relationship_count": 0
    }
    for r in rels:
        t = r.relation_type.lower()
        if t == "called":
            rel_counts["call_count"] += 1
        elif t == "transferred_funds":
            rel_counts["transaction_count"] += 1
        elif t == "visited":
            rel_counts["location_visit_count"] += 1
        elif t == "owns":
            if db.query(ExtractedEntity).filter(ExtractedEntity.id == r.target_entity_id, ExtractedEntity.entity_type == 'PHONE').first():
                rel_counts["shared_phone_count"] += 1
            if db.query(ExtractedEntity).filter(ExtractedEntity.id == r.target_entity_id, ExtractedEntity.entity_type == 'VEHICLE').first():
                rel_counts["shared_vehicle_count"] += 1

    # 3. Graph Analytics (Case Level)
    cga = db.query(CaseGraphAnalytics).filter(CaseGraphAnalytics.case_id == case_id).order_by(CaseGraphAnalytics.created_at.desc()).first()
    
    # 4. Graph Analytics (Entity Level)
    egfs = db.query(EntityGraphFeature).filter(EntityGraphFeature.case_id == case_id).all()
    
    degrees = [f.degree for f in egfs] if egfs else [0]
    betweenness = [f.betweenness_score for f in egfs] if egfs else [0.0]
    
    largest_community = 0
    if egfs:
        community_sizes = {}
        for f in egfs:
            if f.community_id:
                community_sizes[f.community_id] = community_sizes.get(f.community_id, 0) + 1
        if community_sizes:
            largest_community = max(community_sizes.values())

    bridge_candidates = sum(1 for f in egfs if f.bridge_score > 0.3)

    # 5. Temporal
    # Simplistic approximation for synthetic data unless explicit event timestamps exist
    event_span_hours = 0.0
    average_event_gap_hours = 0.0
    rapid_transaction_chain_count = sum(1 for f in egfs if f.transaction_chain_count >= 3)
    repeated_location_window_count = 0 # Not explicitly tracked yet in DB, default 0
    
    # 6. Pattern features (from Alerts)
    alerts = db.query(Alert).filter(Alert.case_id == case_id).all()
    patt_counts = {
        "cross_case_connector_count": 0, "shared_phone_pattern_count": 0,
        "shared_vehicle_pattern_count": 0, "repeated_location_pattern_count": 0,
        "bridge_pattern_count": 0, "high_connectivity_pattern_count": 0
    }
    
    for a in alerts:
        t = a.alert_type
        if t == "CROSS_CASE_CONNECTOR":
            patt_counts["cross_case_connector_count"] += 1
        elif t == "SHARED_PHONE":
            patt_counts["shared_phone_pattern_count"] += 1
        elif t == "SHARED_VEHICLE":
            patt_counts["shared_vehicle_pattern_count"] += 1
        elif t == "RAPID_TRANSACTION_CHAIN":
            pass # Already covered in temporal via feature
        elif t == "BRIDGE_COMMUNITY":
            patt_counts["bridge_pattern_count"] += 1
        elif t == "HIGH_CONNECTIVITY":
            patt_counts["high_connectivity_pattern_count"] += 1

    features_dict = {
        "node_count": cga.node_count if cga else len(entities),
        "edge_count": cga.edge_count if cga else len(rels),
        "graph_density": cga.density if cga else 0.0,
        "connected_component_count": cga.community_count if cga else 1, # approximation
        "community_count": cga.community_count if cga else 1,
        "largest_community_size": largest_community,
        "average_degree": sum(degrees) / len(degrees) if degrees else 0.0,
        "maximum_degree": max(degrees) if degrees else 0,
        "average_betweenness": sum(betweenness) / len(betweenness) if betweenness else 0.0,
        "maximum_betweenness": max(betweenness) if betweenness else 0.0,
        "bridge_candidate_count": bridge_candidates,
        
        **entity_counts,
        **rel_counts,
        
        "event_span_hours": event_span_hours,
        "average_event_gap_hours": average_event_gap_hours,
        "rapid_transaction_chain_count": rapid_transaction_chain_count,
        "repeated_location_window_count": repeated_location_window_count,
        
        **patt_counts
    }

    # Ensure stable ordering
    feature_values = [float(features_dict.get(name, 0.0)) for name in FEATURE_NAMES]
    
    cfv = CaseFeatureVector(
        id=str(uuid.uuid4()),
        case_id=case_id,
        feature_names=FEATURE_NAMES,
        feature_values=feature_values,
        feature_version=FEATURE_VERSION,
        analysis_run_id=analysis_run_id
    )
    
    db.add(cfv)
    db.commit()
    db.refresh(cfv)
    return cfv
