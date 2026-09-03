"""Extraction Pydantic schemas."""
from typing import Literal, List, Optional
from pydantic import BaseModel, Field, field_validator

VerificationStatus = Literal["UNREVIEWED", "ACCEPTED", "REJECTED", "CORRECTED", "NEEDS_MORE_INFORMATION"]
EntityType = Literal["PERSON", "ALIAS", "PHONE", "VEHICLE", "LOCATION", "ORGANIZATION", "BANK_ACCOUNT", "CASE_ID", "DATE", "MONEY"]
RelationshipType = Literal["CALLED", "USED", "OWNS", "VISITED", "TRANSFERRED_TO", "INVOLVED_IN", "MENTIONED_IN", "CONNECTED_TO", "OCCURRED_AT"]

class ExtractedEntityCandidate(BaseModel):
    candidate_id: str = Field(..., description="Stable candidate ID within the document")
    entity_type: EntityType
    original_value: str
    normalized_value: str
    source_document_id: str
    source_text: str
    start_offset: int
    end_offset: int
    confidence: float
    verification_status: VerificationStatus = "UNREVIEWED"
    extraction_provider: str
    extraction_version: str

    @field_validator("confidence")
    def validate_confidence(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @field_validator("start_offset", "end_offset")
    def validate_offsets_non_negative(cls, v):
        if v < 0:
            raise ValueError("Offsets must be non-negative")
        return v

    @field_validator("end_offset")
    def validate_end_offset(cls, v, info):
        if "start_offset" in info.data and v < info.data["start_offset"]:
            raise ValueError("end_offset must be greater than or equal to start_offset")
        return v

    @field_validator("source_text")
    def validate_source_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Source text must be non-empty")
        return v


class ExtractedRelationshipCandidate(BaseModel):
    candidate_id: str = Field(..., description="Stable candidate ID within the document")
    source_candidate_id: str
    relationship_type: RelationshipType
    target_candidate_id: str
    source_document_id: str
    source_text: str
    event_date: Optional[str] = None
    confidence: float
    verification_status: VerificationStatus = "UNREVIEWED"
    extraction_provider: str
    extraction_version: str

    @field_validator("confidence")
    def validate_confidence(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @field_validator("source_text")
    def validate_source_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Source text must be non-empty")
        return v

class DocumentExtractionResult(BaseModel):
    document_id: str
    entities: List[ExtractedEntityCandidate]
    relationships: List[ExtractedRelationshipCandidate]
    provider: str
    version: str

class ReviewDecision(BaseModel):
    verification_status: VerificationStatus
    corrected_value: Optional[str] = None
    rationale: Optional[str] = None

    @field_validator("corrected_value")
    def validate_corrected_value(cls, v, info):
        status = info.data.get("verification_status")
        if status == "CORRECTED" and not v:
            raise ValueError("corrected_value is required when status is CORRECTED")
        return v

    @field_validator("rationale")
    def validate_rationale(cls, v, info):
        status = info.data.get("verification_status")
        if status in ["CORRECTED", "NEEDS_MORE_INFORMATION"] and not v:
            raise ValueError("rationale is required when status is CORRECTED or NEEDS_MORE_INFORMATION")
        return v
