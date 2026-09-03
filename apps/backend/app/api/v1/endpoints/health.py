"""Health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.backend.app.core.config import settings

router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(description="Current status of the service")
    timestamp: str = Field(description="Current UTC timestamp in ISO-8601 format")
    service: str = Field(description="Service identifier")
    version: str = Field(description="Service semantic version")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "timestamp": "2026-09-02T20:00:00+00:00",
                    "service": "SIH 26189 Criminal Network Analysis System",
                    "version": "0.1.0",
                }
            ]
        }
    }


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check endpoint",
    description="Returns current health status, UTC timestamp, service name, and version.",
)
async def health_check() -> HealthCheckResponse:
    """Return system health status."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service=settings.APP_NAME,
        version="0.1.0",
    )
