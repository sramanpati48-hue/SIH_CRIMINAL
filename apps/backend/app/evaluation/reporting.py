"""Evaluation Reporting Schemas."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from apps.backend.app.evaluation.entity_metrics import EntityEvaluationMetrics
from apps.backend.app.evaluation.relationship_metrics import RelationshipEvaluationMetrics


class ConfidenceDistribution(BaseModel):
    LOW: int  # 0.00 to 0.59
    MEDIUM: int  # 0.60 to 0.84
    HIGH: int  # 0.85 to 1.00


class ProviderComparisonItem(BaseModel):
    provider: str
    provider_status: str
    provider_version: str
    model_version: str
    extraction_version: str
    post_processing_version: str
    relationship_rule_version: str
    entity_metrics: Optional[EntityEvaluationMetrics] = None
    relationship_metrics: Optional[RelationshipEvaluationMetrics] = None
    confidence_distribution: Optional[ConfidenceDistribution] = None
    warnings: List[str]
    limitations: List[str]


class ProviderComparisonResult(BaseModel):
    dataset_version: str
    test_document_ids: List[str]
    evaluation_timestamp: str
    providers: List[ProviderComparisonItem]


class ExtractionEvaluationReport(BaseModel):
    provider: str
    provider_status: str
    provider_version: str
    model_version: str
    extraction_version: str
    post_processing_version: str
    relationship_rule_version: str
    dataset_version: str
    test_document_ids: List[str]
    evaluation_timestamp: str
    entity_metrics: Optional[EntityEvaluationMetrics] = None
    relationship_metrics: Optional[RelationshipEvaluationMetrics] = None
    confidence_distribution: Optional[ConfidenceDistribution] = None
    warnings: List[str]
    limitations: List[str]
