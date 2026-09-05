from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # General App Settings
    APP_NAME: str = "SIH 26189 Criminal Network Analysis System"
    APP_ENV: str = Field(default="development", description="Application environment")
    API_PREFIX: str = Field(default="/api/v1", description="Global API version prefix")
    API_HOST: str = Field(default="0.0.0.0", description="Host to bind the API server")
    API_PORT: int = Field(default=8000, description="Port to bind the API server")
    SECRET_KEY: str = Field(
        default="dev_secret_key_change_in_production_min32chars!",
        description="Application secret key",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="Access token expiration in minutes",
    )

    # Password Policy
    BCRYPT_ROUNDS: int = 12
    MIN_PASSWORD_LENGTH: int = 8
    MAX_BCRYPT_PASSWORD_BYTES: int = 72

    # PostgreSQL connection — synchronous driver for the prototype.
    # Override with a real PostgreSQL URL in production:
    #   DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
    DATABASE_URL: str = Field(
        default="sqlite:///./sih_dev.db",
        description="SQLAlchemy database connection string",
    )

    # Neo4j Graph Database (future milestone)
    NEO4J_URI: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j Bolt connection URI",
    )
    NEO4J_USER: str = Field(
        default="neo4j",
        description="Neo4j username",
    )
    NEO4J_PASSWORD: str = Field(
        default="neo4j_dev_password",
        description="Neo4j password",
    )
    NEO4J_DATABASE: str = Field(
        default="neo4j",
        description="Neo4j database name (e.g., 'neo4j' or 'system')",
    )

    # CORS & Security
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Allowed CORS origin for frontend application",
    )

    # Development reviewer identity.
    # Used as the reviewer_id for human-review actions when no authentication
    # system is active.  Must be replaced by a real authenticated identity in
    # any production or staging deployment.  Set via the DEV_REVIEWER_ID
    # environment variable.  A None value means the variable was not
    # configured; callers must handle this explicitly.
    DEV_REVIEWER_ID: Optional[str] = Field(
        default=None,
        description=(
            "Reviewer identity used in development mode when authentication "
            "is not available.  Configure via DEV_REVIEWER_ID env var.  "
            "Never hardcode a fallback value in application logic."
        ),
    )

    # Extraction
    EXTRACTION_PROVIDER: str = Field(
        default="MOCK",
        description=(
            "Active NER provider. Allow-listed values: MOCK, SPACY_BASELINE, SPACY_CUSTOM. "
            "SPACY_CUSTOM requires SPACY_CUSTOM_MODEL_ID to be set."
        ),
    )

    # Model artifact storage — server-side only, never exposed to the frontend.
    # Set to a directory on a local volume with restricted permissions.
    MODEL_ARTIFACT_ROOT: str = Field(
        default="data/training/models",
        description=(
            "Trusted root directory for model artifacts. All model paths are resolved "
            "relative to this directory. Never expose this value in API responses or logs."
        ),
    )

    # ID of the custom spaCy model to load when EXTRACTION_PROVIDER=SPACY_CUSTOM.
    # Must be a registry model_id, not a filesystem path.
    SPACY_CUSTOM_MODEL_ID: Optional[str] = Field(
        default=None,
        description=(
            "Registry model_id for the custom spaCy model. "
            "This is an opaque identifier, not a filesystem path."
        ),
    )

    # NER training gate. Must be explicitly set to true to allow CLI training.
    NER_TRAINING_ENABLED: bool = Field(
        default=False,
        description=(
            "Set to true to allow running the spaCy NER training CLI. "
            "Training via API endpoints is always disabled regardless of this flag."
        ),
    )

    # Subprocess timeout for spaCy training in seconds.
    NER_TRAINING_TIMEOUT_SECONDS: int = Field(
        default=3600,
        description="Maximum wall-clock seconds for a spaCy training subprocess.",
    )


settings = Settings()
