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


settings = Settings()
