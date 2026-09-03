"""Pydantic schemas for Case request/response models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    """Valid case statuses."""

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class CasePriority(str, Enum):
    """Valid case priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# --- Request Schemas ---


class CaseCreate(BaseModel):
    """Schema for creating a new case."""

    case_number: str = Field(
        ..., min_length=1, max_length=100, description="Unique case identifier"
    )
    title: str = Field(
        ..., min_length=1, max_length=255, description="Case title"
    )
    description: str | None = Field(
        default=None, description="Case description"
    )
    priority: CasePriority = Field(
        default=CasePriority.MEDIUM, description="Case priority level"
    )


class CaseUpdate(BaseModel):
    """Schema for updating an existing case (partial update)."""

    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    status: CaseStatus | None = Field(default=None)
    priority: CasePriority | None = Field(default=None)


# --- Response Schemas ---


class CaseResponse(BaseModel):
    """Schema for case responses."""

    id: str
    case_number: str
    title: str
    description: str | None = None
    status: str
    priority: str
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    """Schema for paginated case list responses."""

    total: int
    cases: list[CaseResponse]
