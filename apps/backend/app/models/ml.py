"""Machine Learning SQLAlchemy models."""

from sqlalchemy import ForeignKey, Index, String, Integer, Float, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CaseFeatureVector(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Deterministic feature vector representation of a case for similarity and ML."""
    __tablename__ = "case_feature_vectors"

    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    feature_names: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    feature_values: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    
    feature_version: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_run_id: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index("ix_cfv_case_id", "case_id"),
        Index("ix_cfv_feature_version", "feature_version"),
        Index("ix_cfv_analysis_run_id", "analysis_run_id"),
        Index("ix_cfv_created_at", "created_at"),
    )


class ModelPrediction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Outputs from ML baselines (Anomaly or Priority)."""
    __tablename__ = "model_predictions"

    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'anomaly', 'priority', 'pattern'
    prediction: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    top_features: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_version: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_run_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="OPEN") # e.g. OPEN, ACCEPTED, REJECTED
    requires_human_verification: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("ix_mp_case_id", "case_id"),
        Index("ix_mp_entity_id", "entity_id"),
        Index("ix_mp_prediction_type", "prediction_type"),
        Index("ix_mp_model_version", "model_version"),
        Index("ix_mp_created_at", "created_at"),
    )


class SimilarityResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores historical case similarity pairs."""
    __tablename__ = "similarity_results"

    current_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    similar_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_features: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    differing_features: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    
    feature_version: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_run_id: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        Index("ix_sr_current_case_id", "current_case_id"),
        Index("ix_sr_similar_case_id", "similar_case_id"),
        Index("ix_sr_analysis_run_id", "analysis_run_id"),
        Index("ix_sr_created_at", "created_at"),
    )

class ModelArtifact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Securely stores and tracks physical ML artifacts (e.g. joblib files)."""
    
    __tablename__ = "model_artifacts"
    
    artifact_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_version: Mapped[str] = mapped_column(String(100), nullable=False)
    
    artifact_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    
    scikit_learn_version: Mapped[str] = mapped_column(String(50), nullable=False)
    python_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    feature_names: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    training_case_ids: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    hyperparameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="READY") # READY | CHECKSUM_INVALID | MISSING | INCOMPATIBLE | REJECTED

    __table_args__ = (
        Index("ix_model_artifacts_versions", "model_version", "dataset_version"),
        Index("ix_model_artifacts_status", "status"),
    )
