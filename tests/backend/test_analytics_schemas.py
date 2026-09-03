"""Tests for Analytics schemas."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from apps.backend.app.analytics.schemas import EntityGraphFeatures, PatternAlert, AlertSeverity, AnalyticsStatus


def test_entity_graph_features_validation():
    """Test schema validation bounds."""
    # Valid
    feat = EntityGraphFeatures(
        entity_id="E1",
        case_id="C1",
        entity_type="PERSON",
        degree=10,
        in_degree=5,
        out_degree=5,
        case_count=1,
        unique_neighbour_count=8,
        shared_location_count=2,
        shared_phone_count=1,
        shared_vehicle_count=0,
        transaction_count=0,
        transaction_total=0.0,
        transaction_chain_count=0,
        pagerank_score=0.5,
        betweenness_score=0.2,
        bridge_score=0.1,
        computed_at=datetime.now(timezone.utc),
        algorithm_version="v1",
        analytics_engine="test"
    )
    assert feat.degree == 10
    
    # Invalid bounds
    with pytest.raises(ValidationError):
        EntityGraphFeatures(
            entity_id="E1",
            case_id="C1",
            entity_type="PERSON",
            degree=-1, # Invalid
            computed_at=datetime.now(timezone.utc),
            algorithm_version="v1",
            analytics_engine="test"
        )
        
    with pytest.raises(ValidationError):
        EntityGraphFeatures(
            entity_id="E1",
            case_id="C1",
            entity_type="PERSON",
            pagerank_score=1.5, # Invalid > 1.0
            computed_at=datetime.now(timezone.utc),
            algorithm_version="v1",
            analytics_engine="test"
        )
