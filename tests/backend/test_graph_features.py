"""Tests for python fallback graph feature extraction."""

import datetime
from apps.backend.app.graph.schema import GraphResponse, GraphNode, GraphEdge
from apps.backend.app.analytics.fallback import NetworkXFeatureExtractor

def test_feature_extractor():
    # Build a simple synthetic graph
    n1 = GraphNode(id="n1", label="PERSON", entity_type="PERSON", properties={})
    n2 = GraphNode(id="n2", label="PHONE", entity_type="PHONE", properties={})
    n3 = GraphNode(id="n3", label="PERSON", entity_type="PERSON", properties={})
    e1 = GraphEdge(id="e1", source_id="n1", target_id="n2", relationship_type="OWNS")
    e2 = GraphEdge(id="e2", source_id="n3", target_id="n2", relationship_type="CALLED")
    
    response = GraphResponse(
        case_id="C1",
        nodes=[n1, n2, n3],
        edges=[e1, e2],
        generated_at=datetime.datetime.now(datetime.timezone.utc),
        truncated=False
    )
    
    extractor = NetworkXFeatureExtractor(response)
    features, case_analytics = extractor.extract_features()
    
    assert case_analytics.node_count == 3
    assert case_analytics.edge_count == 2
    
    assert features["n1"].degree == 1
    assert features["n2"].degree == 2 # 2 edges incident
    assert features["n3"].degree == 1
    
    # n1 and n3 should have shared_phone_count == 1 because n2 is a PHONE
    assert features["n1"].shared_phone_count == 1
    assert features["n3"].shared_phone_count == 1
