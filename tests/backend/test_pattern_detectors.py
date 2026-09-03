"""Tests for pattern detectors."""

import datetime
from apps.backend.app.graph.schema import GraphResponse, GraphNode, GraphEdge
from apps.backend.app.analytics.fallback import NetworkXFeatureExtractor
from apps.backend.app.analytics.detectors import SharedPhoneDetector, CrossCaseConnectorDetector, RapidTransactionChainDetector


def test_shared_phone_detector():
    n1 = GraphNode(id="p1", label="PERSON", entity_type="PERSON", properties={})
    n2 = GraphNode(id="p2", label="PERSON", entity_type="PERSON", properties={})
    n3 = GraphNode(id="phone1", label="PHONE", entity_type="PHONE", properties={"phone_number": "555-0100"})
    
    e1 = GraphEdge(id="e1", source_id="p1", target_id="phone1", relationship_type="OWNS", source_document_id="doc1")
    e2 = GraphEdge(id="e2", source_id="p2", target_id="phone1", relationship_type="CALLED", source_document_id="doc2")
    
    response = GraphResponse(
        case_id="C1",
        nodes=[n1, n2, n3],
        edges=[e1, e2],
        generated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    
    extractor = NetworkXFeatureExtractor(response)
    features, _ = extractor.extract_features()
    
    detector = SharedPhoneDetector()
    alerts = list(detector.detect(response, features, "run1"))
    
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.pattern_type == "SHARED_PHONE"
    assert len(alert.entities_involved) == 3
    assert set(alert.evidence_ids) == {"doc1", "doc2"}


def test_rapid_transaction_chain_detector():
    n1 = GraphNode(id="a1", label="BANK_ACCOUNT", entity_type="BANK_ACCOUNT", properties={})
    n2 = GraphNode(id="a2", label="BANK_ACCOUNT", entity_type="BANK_ACCOUNT", properties={})
    n3 = GraphNode(id="a3", label="BANK_ACCOUNT", entity_type="BANK_ACCOUNT", properties={})
    n4 = GraphNode(id="a4", label="BANK_ACCOUNT", entity_type="BANK_ACCOUNT", properties={})
    
    e1 = GraphEdge(id="e1", source_id="a1", target_id="a2", relationship_type="TRANSFERRED_TO", source_document_id="d1")
    e2 = GraphEdge(id="e2", source_id="a2", target_id="a3", relationship_type="TRANSFERRED_TO", source_document_id="d2")
    e3 = GraphEdge(id="e3", source_id="a2", target_id="a4", relationship_type="TRANSFERRED_TO", source_document_id="d3")
    
    response = GraphResponse(
        case_id="C1",
        nodes=[n1, n2, n3, n4],
        edges=[e1, e2, e3],
        generated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    
    extractor = NetworkXFeatureExtractor(response)
    features, _ = extractor.extract_features()
    
    detector = RapidTransactionChainDetector()
    alerts = list(detector.detect(response, features, "run1"))
    
    # Only middle accounts a2 and a3 are pass-throughs
    assert len(alerts) >= 1
    types = [a.pattern_type for a in alerts]
    assert "RAPID_TRANSACTION_CHAIN" in types
