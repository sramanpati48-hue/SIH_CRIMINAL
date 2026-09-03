"""Pydantic schemas for Document request/response models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Valid document file types."""

    CDR = "CDR"
    TEXT_REPORT = "TEXT_REPORT"
    BANK_STATEMENT = "BANK_STATEMENT"
    LOCATION_LOG = "LOCATION_LOG"
    VEHICLE_LOG = "VEHICLE_LOG"
    OTHER = "OTHER"


class DocumentStatus(str, Enum):
    """Valid document processing statuses."""

    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


# --- Request Schemas ---


class DocumentCreate(BaseModel):
    """Schema for creating a document record."""

    file_name: str = Field(
        ..., min_length=1, max_length=255, description="Original file name"
    )
    file_type: DocumentType = Field(
        ..., description="Type of evidence document"
    )
    raw_content: str | None = Field(
        default=None, description="Raw text content of the document"
    )


# --- Response Schemas ---


class DocumentResponse(BaseModel):
    """Schema for document responses."""

    id: str
    case_id: str
    file_name: str
    file_type: str
    file_hash: str | None = None
    status: str
    uploaded_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Schema for document list responses."""

    total: int
    documents: list[DocumentResponse]
