"""Evidence-backed HTML report generation service."""

import os
from datetime import datetime, timezone
from typing import List, Any
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader, select_autoescape

from apps.backend.app.models.case import Case
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.alert import Alert
from apps.backend.app.models.user import User
from apps.backend.app.schemas.report import (
    CaseReportContext,
    ReportEntityItem,
    ReportRelationshipItem,
    ReportAlertItem
)


# Evidence Excerpt Policy Limits
REPORT_MAX_EVIDENCE_CHARS = 500
REPORT_MAX_ENTITIES = 500
REPORT_MAX_RELATIONSHIPS = 500
REPORT_MAX_ALERTS = 200

REPORT_VERSION = "1.0"


def truncate_evidence(text: str | None) -> str | None:
    """Safely bound evidence text to a deterministic maximum length."""
    if not text:
        return None
    if len(text) > REPORT_MAX_EVIDENCE_CHARS:
        return text[:REPORT_MAX_EVIDENCE_CHARS] + "..."
    return text


class ReportService:
    """Service to construct and render evidence-backed HTML case reports."""

    def __init__(self, db: Session):
        self.db = db
        # Configure strict, secure Jinja environment
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_html_report(self, case_id: str, current_user: User) -> tuple[str, dict[str, Any]]:
        """
        Generate the HTML report for a case in memory.
        Returns the HTML string and metadata for audit logging.
        """
        # Fetch Case
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Fetch Entities (ACCEPTED or CORRECTED)
        entities_query = (
            self.db.query(ExtractedEntity)
            .filter(
                ExtractedEntity.case_id == case_id,
                ExtractedEntity.verification_status.in_(["ACCEPTED", "CORRECTED"])
            )
            .limit(REPORT_MAX_ENTITIES)
        )
        entities = entities_query.all()
        entity_items = [
            ReportEntityItem(
                id=e.id,
                display_value=e.original_value or e.canonical_name,
                normalized_value=e.canonical_name,
                entity_type=e.entity_type,
                verification_status=e.verification_status,
                confidence=float(e.confidence_score) if e.confidence_score is not None else None,
                source_document_id=e.document_id,
                source_record_id=e.source_record_id,
            ) for e in entities
        ]

        # Fetch Relationships (ACCEPTED or CORRECTED)
        # We also need the target and source entities' display values.
        # Since these are verified relationships, their source/target entities might not all be loaded 
        # in the relationships object directly, but we can query them or just load from relationship if 
        # joined. For simplicity, let's load them and map IDs.
        entity_map = {e.id: (e.original_value or e.canonical_name) for e in entities}
        
        # If a relationship is verified, its source/target must exist, but they might not be in our limited entity list.
        # So we query them properly.
        rels_query = (
            self.db.query(ExtractedRelationship)
            .filter(
                ExtractedRelationship.case_id == case_id,
                ExtractedRelationship.verification_status.in_(["ACCEPTED", "CORRECTED"])
            )
            .limit(REPORT_MAX_RELATIONSHIPS)
        )
        rels = rels_query.all()
        
        # Load any missing entity names for relationships
        missing_entity_ids = set()
        for r in rels:
            if r.source_entity_id not in entity_map:
                missing_entity_ids.add(r.source_entity_id)
            if r.target_entity_id not in entity_map:
                missing_entity_ids.add(r.target_entity_id)
                
        if missing_entity_ids:
            extra_entities = self.db.query(ExtractedEntity).filter(ExtractedEntity.id.in_(missing_entity_ids)).all()
            for e in extra_entities:
                entity_map[e.id] = (e.original_value or e.canonical_name)

        rel_items = []
        for r in rels:
            snippet = truncate_evidence(r.source_text_snippet)
            rel_items.append(
                ReportRelationshipItem(
                    id=r.id,
                    source_entity_display=entity_map.get(r.source_entity_id, "Unknown Entity"),
                    target_entity_display=entity_map.get(r.target_entity_id, "Unknown Entity"),
                    relationship_type=r.relation_type,
                    event_date=str(r.event_timestamp) if r.event_timestamp else None,
                    confidence=float(r.confidence_score) if r.confidence_score is not None else None,
                    verification_status=r.verification_status,
                    source_document_id=r.document_id,
                    bounded_evidence_excerpt=snippet,
                    evidence_available=bool(snippet)
                )
            )

        # Fetch Alerts (OPEN or ACCEPTED)
        alerts_query = (
            self.db.query(Alert)
            .filter(
                Alert.case_id == case_id,
                Alert.status.in_(["OPEN", "ACCEPTED", "CORRECTED"])
            )
            .limit(REPORT_MAX_ALERTS)
        )
        alerts = alerts_query.all()
        alert_items = [
            ReportAlertItem(
                id=a.id,
                alert_type=a.alert_type,
                severity=a.severity,
                title=a.title,
                explanation=a.description,
                status=a.status,
                requires_human_verification=a.requires_human_verification,
                rule_version=a.rule_version,
                model_version=a.model_version,
                evidence_references=str(a.evidence_ids) if a.evidence_ids else None
            ) for a in alerts
        ]

        context = CaseReportContext(
            case_number=case.case_number,
            title=case.title,
            status=case.status,
            priority=case.priority,
            created_at=str(case.created_at) if case.created_at else None,
            report_generated_at=datetime.now(timezone.utc).isoformat(),
            report_version=REPORT_VERSION,
            entities=entity_items,
            relationships=rel_items,
            alerts=alert_items
        )

        template = self.env.get_template("report_template.html")
        html_content = template.render(context.model_dump())

        metadata = {
            "report_version": REPORT_VERSION,
            "case_id": case_id,
            "entity_count": len(entity_items),
            "relationship_count": len(rel_items),
            "alert_count": len(alert_items),
            "report_generated": True
        }

        return html_content, metadata
