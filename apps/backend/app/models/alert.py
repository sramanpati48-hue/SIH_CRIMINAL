"""Alert SQLAlchemy model."""

from datetime import datetime
from sqlalchemy import ForeignKey, Index, Numeric, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Alert(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """System-generated investigative alert requiring human review."""

    __tablename__ = "alerts"

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # FINANCIAL_LOOP | BURNER_PHONE | CO_LOCATION | HIGH_CENTRALITY
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="MEDIUM"
    )  # LOW | MEDIUM | HIGH | CRITICAL
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    source_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)  # Legacy
    evidence_ids: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    feature_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rule_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    analytics_engine: Mapped[str | None] = mapped_column(String(50), nullable=True)
    algorithm_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    analysis_run_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requires_human_verification: Mapped[bool] = mapped_column(default=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="OPEN"
    )  # OPEN | ACCEPTED | REJECTED | CORRECTED | NEEDS_MORE_INFORMATION

    __table_args__ = (
        Index("ix_alerts_case_id", "case_id"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_alert_type", "alert_type"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_created_at", "created_at"),
        Index("ix_alerts_analysis_run_id", "analysis_run_id"),
    )
