"""Analytics SQLAlchemy models."""

from sqlalchemy import ForeignKey, Index, Numeric, String, Text, Integer, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EntityGraphFeature(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores computed graph features for a single entity."""
    __tablename__ = "entity_graph_features"

    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Degree metrics
    degree: Mapped[int] = mapped_column(Integer, default=0)
    in_degree: Mapped[int | None] = mapped_column(Integer, nullable=True)
    out_degree: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Specific counts
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    unique_neighbour_count: Mapped[int] = mapped_column(Integer, default=0)
    shared_location_count: Mapped[int] = mapped_column(Integer, default=0)
    shared_phone_count: Mapped[int] = mapped_column(Integer, default=0)
    shared_vehicle_count: Mapped[int] = mapped_column(Integer, default=0)

    # Transactions
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    transaction_total: Mapped[float] = mapped_column(Float, default=0.0)
    transaction_chain_count: Mapped[int] = mapped_column(Integer, default=0)

    # Graph structural properties
    community_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    community_size: Mapped[int] = mapped_column(Integer, default=0)
    pagerank_score: Mapped[float] = mapped_column(Float, default=0.0)
    betweenness_score: Mapped[float] = mapped_column(Float, default=0.0)
    bridge_score: Mapped[float] = mapped_column(Float, default=0.0)
    historical_similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Metadata
    algorithm_version: Mapped[str] = mapped_column(String(50), nullable=False)
    analytics_engine: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_run_id: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index("ix_egf_case_id", "case_id"),
        Index("ix_egf_entity_id", "entity_id"),
        Index("ix_egf_analysis_run_id", "analysis_run_id"),
        Index("ix_egf_created_at", "created_at"),
    )


class CaseGraphAnalytics(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Aggregate graph analytics for a case."""
    __tablename__ = "case_graph_analytics"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, default=0)
    community_count: Mapped[int] = mapped_column(Integer, default=0)
    density: Mapped[float] = mapped_column(Float, default=0.0)

    algorithm_version: Mapped[str] = mapped_column(String(50), nullable=False)
    analytics_engine: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_run_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    truncated: Mapped[bool] = mapped_column(Boolean, default=False)
    warnings: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_cga_case_id", "case_id"),
        Index("ix_cga_analysis_run_id", "analysis_run_id"),
        Index("ix_cga_created_at", "created_at"),
    )
