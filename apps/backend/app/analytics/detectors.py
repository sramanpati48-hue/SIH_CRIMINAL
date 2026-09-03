"""Graph pattern detectors (Explainable Rules)."""

import uuid
import datetime
import networkx as nx
from typing import Iterator

from apps.backend.app.graph.schema import GraphResponse
from apps.backend.app.analytics.schemas import PatternAlert, AlertSeverity, AlertStatus, EntityGraphFeatures
from apps.backend.app.analytics.config import analytics_settings
from apps.backend.app.analytics.fallback import NetworkXFeatureExtractor


class BaseDetector:
    """Base class for all pattern detectors."""
    
    PATTERN_TYPE = "UNKNOWN"
    TITLE = "Unknown Pattern"
    VERSION = analytics_settings.ANALYTICS_RULE_VERSION

    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        raise NotImplementedError


class SharedPhoneDetector(BaseDetector):
    """Detects when multiple people share the same phone."""
    PATTERN_TYPE = "SHARED_PHONE"
    TITLE = "Shared Phone Number"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        G = NetworkXFeatureExtractor(graph_response).G
        phones = [n for n, d in G.nodes(data=True) if d.get("entity_type") == "PHONE"]
        
        for phone_id in phones:
            phone_data = G.nodes[phone_id]
            people_ids = set()
            evidence_ids = set()
            
            for u, v, k in G.in_edges(phone_id, data=True):
                if G.nodes[u].get("entity_type") == "PERSON":
                    people_ids.add(u)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
            for u, v, k in G.out_edges(phone_id, data=True):
                if G.nodes[v].get("entity_type") == "PERSON":
                    people_ids.add(v)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
                    
            if len(people_ids) >= analytics_settings.MIN_SHARED_PHONE:
                score = min(1.0, len(people_ids) / 5.0)
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.HIGH if len(people_ids) > 3 else AlertSeverity.MEDIUM,
                    score=score,
                    title=self.TITLE,
                    explanation=f"Phone {phone_data.get('properties', {}).get('phone_number', phone_id)} is shared by {len(people_ids)} individuals. This is an investigative lead requiring human verification.",
                    entities_involved=list(people_ids) + [phone_id],
                    evidence_ids=list(evidence_ids),
                    feature_values={"shared_count": len(people_ids), "phone_id": phone_id},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class CrossCaseConnectorDetector(BaseDetector):
    """Detects entities that connect multiple cases."""
    PATTERN_TYPE = "CROSS_CASE_CONNECTOR"
    TITLE = "Cross-Case Connector"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        G = NetworkXFeatureExtractor(graph_response).G
        cases = [n for n, d in G.nodes(data=True) if d.get("entity_type") == "CASE"]
        if len(cases) < 2: return
            
        for node_id, data in G.nodes(data=True):
            if data.get("entity_type") == "CASE": continue
            connected_cases = set()
            evidence_ids = set()
            
            for u, v, k in G.edges(node_id, data=True):
                if v in cases:
                    connected_cases.add(v)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
            for u, v, k in G.in_edges(node_id, data=True):
                if u in cases:
                    connected_cases.add(u)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
                        
            if len(connected_cases) >= analytics_settings.MIN_CASES_CROSS_CONNECTOR:
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.HIGH,
                    score=0.8,
                    title=self.TITLE,
                    explanation=f"Entity {node_id} connects {len(connected_cases)} synthetic cases. This is an investigative lead requiring human verification.",
                    entities_involved=[node_id] + list(connected_cases),
                    evidence_ids=list(evidence_ids),
                    feature_values={"connected_cases_count": len(connected_cases)},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class HighConnectivityDetector(BaseDetector):
    """Detects highly connected nodes."""
    PATTERN_TYPE = "HIGH_CONNECTIVITY"
    TITLE = "Highly Connected Entity"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        if not features: return
        degrees = sorted([f.degree for f in features.values()])
        idx = int(len(degrees) * analytics_settings.HIGH_CONNECTIVITY_PERCENTILE)
        threshold = max(degrees[idx] if degrees else 0, 5)
            
        for node_id, feat in features.items():
            if feat.entity_type in ("CASE", "DOCUMENT", "EVENT"): continue
            if feat.degree >= threshold:
                G = NetworkXFeatureExtractor(graph_response).G
                evidence_ids = set()
                for u, v, k in G.edges(node_id, data=True):
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
                for u, v, k in G.in_edges(node_id, data=True):
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
                    
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.MEDIUM,
                    score=0.7,
                    title=self.TITLE,
                    explanation=f"Entity {node_id} has a high degree of connectivity ({feat.degree} links). This is a structural metric requiring context, not proof of criminality.",
                    entities_involved=[node_id],
                    evidence_ids=list(evidence_ids),
                    feature_values={"degree": feat.degree, "threshold": threshold},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class SharedVehicleDetector(BaseDetector):
    PATTERN_TYPE = "SHARED_VEHICLE"
    TITLE = "Shared Vehicle"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        G = NetworkXFeatureExtractor(graph_response).G
        vehicles = [n for n, d in G.nodes(data=True) if d.get("entity_type") == "VEHICLE"]
        for v_id in vehicles:
            people_ids = set()
            evidence_ids = set()
            for u, v, k in G.in_edges(v_id, data=True):
                if G.nodes[u].get("entity_type") == "PERSON":
                    people_ids.add(u)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
            for u, v, k in G.out_edges(v_id, data=True):
                if G.nodes[v].get("entity_type") == "PERSON":
                    people_ids.add(v)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
            if len(people_ids) >= analytics_settings.MIN_SHARED_VEHICLE:
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.MEDIUM,
                    score=0.6,
                    title=self.TITLE,
                    explanation=f"Vehicle {v_id} is associated with {len(people_ids)} individuals. Investigative lead requiring verification.",
                    entities_involved=list(people_ids) + [v_id],
                    evidence_ids=list(evidence_ids),
                    feature_values={"shared_count": len(people_ids)},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class RepeatedLocationDetector(BaseDetector):
    PATTERN_TYPE = "REPEATED_LOCATION"
    TITLE = "Repeated Location Association"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        G = NetworkXFeatureExtractor(graph_response).G
        locations = [n for n, d in G.nodes(data=True) if d.get("entity_type") == "LOCATION"]
        for loc_id in locations:
            # We look for people with multiple edges to the same location, or multiple people to the same location.
            # A simplified fallback for MVP: if location has >= MIN_REPEATED_LOCATION_EVENTS incident edges from persons
            evidence_ids = set()
            person_events = []
            for u, v, k in G.in_edges(loc_id, data=True):
                if G.nodes[u].get("entity_type") == "PERSON":
                    person_events.append(u)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
            for u, v, k in G.out_edges(loc_id, data=True):
                if G.nodes[v].get("entity_type") == "PERSON":
                    person_events.append(v)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
            
            if len(person_events) >= analytics_settings.MIN_REPEATED_LOCATION_EVENTS:
                unique_people = set(person_events)
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.MEDIUM,
                    score=0.6,
                    title=self.TITLE,
                    explanation=f"Location {loc_id} appears in {len(person_events)} events involving {len(unique_people)} people. Investigative lead requiring verification.",
                    entities_involved=list(unique_people) + [loc_id],
                    evidence_ids=list(evidence_ids),
                    feature_values={"event_count": len(person_events)},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class RapidTransactionChainDetector(BaseDetector):
    PATTERN_TYPE = "RAPID_TRANSACTION_CHAIN"
    TITLE = "Rapid Transaction Chain"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        G = NetworkXFeatureExtractor(graph_response).G
        accounts = [n for n, d in G.nodes(data=True) if d.get("entity_type") == "BANK_ACCOUNT"]
        
        # Simplified chain detection: node has in-degree of TRANSFER and out-degree of TRANSFER
        for acc in accounts:
            in_tx = [e for e in G.in_edges(acc, data=True) if e[2].get("relationship_type") == "TRANSFERRED_TO"]
            out_tx = [e for e in G.out_edges(acc, data=True) if e[2].get("relationship_type") == "TRANSFERRED_TO"]
            
            if len(in_tx) > 0 and len(out_tx) > 0 and (len(in_tx) + len(out_tx) >= analytics_settings.MIN_TRANSACTION_CHAIN_LENGTH):
                evidence_ids = set()
                entities = {acc}
                for u, v, k in in_tx + out_tx:
                    entities.add(u)
                    entities.add(v)
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
                    
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.HIGH,
                    score=0.8,
                    title=self.TITLE,
                    explanation=f"Account {acc} acts as a pass-through in a transaction chain of length {len(in_tx) + len(out_tx)}. Requires human verification.",
                    entities_involved=list(entities),
                    evidence_ids=list(evidence_ids),
                    feature_values={"chain_length": len(in_tx) + len(out_tx)},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class BridgeBetweenCommunitiesDetector(BaseDetector):
    PATTERN_TYPE = "BRIDGE_COMMUNITIES"
    TITLE = "Community Bridge Entity"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        # Using feature pre-computed bridge_score (betweenness)
        if not features: return
        scores = [f.bridge_score for f in features.values() if f.bridge_score > 0]
        if not scores: return
        scores.sort()
        # Top 5% betweenness are bridge candidates
        threshold = scores[int(len(scores) * 0.95)] if len(scores) > 10 else scores[-1]
        
        for node_id, feat in features.items():
            if feat.entity_type in ("CASE", "DOCUMENT", "EVENT"): continue
            if feat.bridge_score >= threshold and feat.bridge_score > 0.1:
                G = NetworkXFeatureExtractor(graph_response).G
                evidence_ids = set()
                for u, v, k in G.edges(node_id, data=True):
                    if k.get("source_document_id"): evidence_ids.add(k["source_document_id"])
                
                yield PatternAlert(
                    alert_id=str(uuid.uuid4()),
                    case_id=graph_response.case_id or "UNKNOWN_CASE",
                    pattern_type=self.PATTERN_TYPE,
                    severity=AlertSeverity.MEDIUM,
                    score=feat.bridge_score,
                    title=self.TITLE,
                    explanation=f"Entity {node_id} bridges different parts of the network (betweenness {feat.bridge_score:.2f}). Investigative lead requiring human verification.",
                    entities_involved=[node_id],
                    evidence_ids=list(evidence_ids),
                    feature_values={"betweenness": feat.bridge_score},
                    rule_version=self.VERSION,
                    model_version=None,
                    analytics_engine="networkx_fallback",
                    algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                    analysis_run_id=analysis_run_id,
                    status=AlertStatus.OPEN,
                    requires_human_verification=True,
                    created_at=datetime.datetime.now(datetime.timezone.utc)
                )


class HistoricalSimilarityDetector(BaseDetector):
    PATTERN_TYPE = "HISTORICAL_SIMILARITY"
    TITLE = "Historical Case Similarity"
    
    def detect(self, graph_response: GraphResponse, features: dict[str, EntityGraphFeatures], analysis_run_id: str) -> Iterator[PatternAlert]:
        # Placeholder as requested
        return iter([])


ALL_DETECTORS = [
    SharedPhoneDetector(),
    CrossCaseConnectorDetector(),
    HighConnectivityDetector(),
    SharedVehicleDetector(),
    RepeatedLocationDetector(),
    RapidTransactionChainDetector(),
    BridgeBetweenCommunitiesDetector(),
    HistoricalSimilarityDetector()
]
