"""Analytics coordination service."""

import datetime
import hashlib
from typing import Iterator

from apps.backend.app.graph.schema import GraphResponse
from apps.backend.app.analytics.schemas import (
    AnalyticsRunResponse, 
    AnalyticsStatus, 
    AnalyticsEngine, 
    EntityGraphFeatures, 
    CaseGraphAnalytics, 
    PatternAlert
)
from apps.backend.app.analytics.config import analytics_settings
from apps.backend.app.analytics.engine import GraphAnalyticsEngine
from apps.backend.app.analytics.detectors import ALL_DETECTORS


class AnalyticsService:
    """Orchestrates graph feature extraction and pattern detection."""

    def __init__(self, case_id: str):
        self.case_id = case_id
        self.engine = GraphAnalyticsEngine(case_id)

    def _generate_run_id(self, graph_response: GraphResponse) -> str:
        """Generate a deterministic analysis run ID based on case, graph state, and algorithm version."""
        raw = f"{self.case_id}|{graph_response.generated_at.isoformat()}|{analytics_settings.ANALYTICS_ALGORITHM_VERSION}|{analytics_settings.ANALYTICS_RULE_VERSION}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def run_analysis(self, graph_response: GraphResponse | None) -> tuple[AnalyticsRunResponse, dict[str, EntityGraphFeatures], list[PatternAlert]]:
        """Run full analytics pipeline on a subgraph."""
        
        start_time = datetime.datetime.now(datetime.timezone.utc)
        
        if not graph_response:
            # Handle Neo4j Offline
            return AnalyticsRunResponse(
                analysis_run_id="OFFLINE",
                case_id=self.case_id,
                status=AnalyticsStatus.GRAPH_UNAVAILABLE,
                analytics_engine=AnalyticsEngine.NONE,
                gds_available=self.engine._is_gds_available(),
                warnings=["Graph analytics could not run because Neo4j is unavailable."],
                started_at=start_time,
                completed_at=datetime.datetime.now(datetime.timezone.utc)
            ), {}, []
            
        if not graph_response.nodes and not graph_response.edges:
            # Handle empty graph
            return AnalyticsRunResponse(
                analysis_run_id="EMPTY",
                case_id=self.case_id,
                status=AnalyticsStatus.NO_GRAPH_DATA,
                analytics_engine=AnalyticsEngine.NONE,
                gds_available=self.engine._is_gds_available(),
                warnings=["No graph relationships are available for this case."],
                started_at=start_time,
                completed_at=datetime.datetime.now(datetime.timezone.utc)
            ), {}, []

        run_id = self._generate_run_id(graph_response)
        
        try:
            # 1. Extract Features
            features_by_id, case_analytics = self.engine.extract_features(graph_response)
            
            # 2. Run Detectors
            alerts = []
            for detector in ALL_DETECTORS:
                for alert in detector.detect(graph_response, features_by_id, run_id):
                    alerts.append(alert)
                    
            # 3. Formulate Response
            response = AnalyticsRunResponse(
                analysis_run_id=run_id,
                case_id=self.case_id,
                status=case_analytics.status,
                analytics_engine=AnalyticsEngine(case_analytics.analytics_engine),
                gds_available=self.engine._is_gds_available(),
                node_count=case_analytics.node_count,
                edge_count=case_analytics.edge_count,
                feature_count=len(features_by_id),
                alert_count=len(alerts),
                warnings=case_analytics.warnings,
                started_at=start_time,
                completed_at=datetime.datetime.now(datetime.timezone.utc)
            )
            
            return response, features_by_id, alerts
            
        except Exception as e:
            # Handle unexpected failures
            return AnalyticsRunResponse(
                analysis_run_id=run_id,
                case_id=self.case_id,
                status=AnalyticsStatus.FAILED,
                analytics_engine=AnalyticsEngine.NONE,
                gds_available=self.engine._is_gds_available(),
                warnings=[f"Analytics failed: {str(e)}"],
                started_at=start_time,
                completed_at=datetime.datetime.now(datetime.timezone.utc)
            ), {}, []
