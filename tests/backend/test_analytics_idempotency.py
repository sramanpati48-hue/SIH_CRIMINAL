"""Tests for analytics idempotency."""

from unittest.mock import patch
from apps.backend.app.analytics.service import AnalyticsService
from apps.backend.app.analytics.config import analytics_settings
import datetime
from apps.backend.app.graph.schema import GraphResponse

def test_generate_run_id_deterministic():
    service = AnalyticsService(case_id="case123")
    
    dt = datetime.datetime(2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    resp1 = GraphResponse(case_id="case123", nodes=[], edges=[], generated_at=dt)
    resp2 = GraphResponse(case_id="case123", nodes=[], edges=[], generated_at=dt)
    
    id1 = service._generate_run_id(resp1)
    id2 = service._generate_run_id(resp2)
    
    assert id1 == id2
    
    dt3 = datetime.datetime(2025, 1, 1, 12, 0, 1, tzinfo=datetime.timezone.utc)
    resp3 = GraphResponse(case_id="case123", nodes=[], edges=[], generated_at=dt3)
    id3 = service._generate_run_id(resp3)
    
    assert id1 != id3
