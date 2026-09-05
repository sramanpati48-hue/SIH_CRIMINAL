"""Schemas for report generation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ReportEntityItem(BaseModel):
    id: str
    display_value: str
    normalized_value: Optional[str] = None
    entity_type: str
    verification_status: str
    confidence: Optional[float] = None
    source_document_id: Optional[str] = None
    source_record_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportRelationshipItem(BaseModel):
    id: str
    source_entity_display: str
    target_entity_display: str
    relationship_type: str
    event_date: Optional[str] = None
    confidence: Optional[float] = None
    verification_status: str
    source_document_id: Optional[str] = None
    bounded_evidence_excerpt: Optional[str] = None
    evidence_available: bool = False

    model_config = ConfigDict(from_attributes=True)


class ReportAlertItem(BaseModel):
    id: str
    alert_type: str
    severity: str
    title: str
    explanation: Optional[str] = None
    status: str
    requires_human_verification: bool
    rule_version: Optional[str] = None
    model_version: Optional[str] = None
    evidence_references: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CaseReportContext(BaseModel):
    case_number: str
    title: str
    status: str
    priority: str
    created_at: Optional[str] = None
    report_generated_at: str
    report_version: str
    entities: List[ReportEntityItem]
    relationships: List[ReportRelationshipItem]
    alerts: List[ReportAlertItem]

    model_config = ConfigDict(from_attributes=True)


class ReportExportMetadata(BaseModel):
    report_version: str
    case_id: str
    entity_count: int
    relationship_count: int
    alert_count: int
    report_generated: bool
