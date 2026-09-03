"""Ingestion Pydantic schemas representing expected CSV/JSON structures."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from apps.backend.app.ingestion.validators import validate_positive_amount, validate_non_empty_string

class BaseIngestionRecord(BaseModel):
    """Base configuration for ingestion records to reject extra fields."""
    model_config = ConfigDict(extra="forbid")
    
    case_id: str = Field(..., description="Target Case ID")

    @field_validator("case_id", mode="after")
    @classmethod
    def check_case_id(cls, v: str) -> str:
        return validate_non_empty_string(v, type('Info', (), {'field_name': 'case_id'})())


class PersonRecord(BaseIngestionRecord):
    person_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    alias: Optional[str] = None
    dob: Optional[str] = None

    @field_validator("person_id", "name", mode="after")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        return validate_non_empty_string(v, type('Info', (), {'field_name': 'field'})())


class CaseRecord(BaseModel):
    # Case records define cases, they don't belong to a case_id in the same way, they ARE the case
    model_config = ConfigDict(extra="forbid")
    case_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    status: str = Field(...)
    opened_at: str = Field(...)


class PhoneRecord(BaseIngestionRecord):
    phone_id: str = Field(..., min_length=1)
    number: str = Field(..., min_length=1)
    owner_person_id: Optional[str] = None


class VehicleRecord(BaseIngestionRecord):
    vehicle_id: str = Field(..., min_length=1)
    plate: str = Field(..., min_length=1)
    owner_person_id: Optional[str] = None


class LocationRecord(BaseIngestionRecord):
    location_id: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)


class CallRecord(BaseIngestionRecord):
    caller_phone_id: str = Field(..., min_length=1)
    receiver_phone_id: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)
    duration_seconds: int = Field(ge=0)


class TransactionRecord(BaseIngestionRecord):
    transaction_id: str = Field(..., min_length=1)
    source_account: str = Field(..., min_length=1)
    target_account: str = Field(..., min_length=1)
    amount: float = Field(...)
    timestamp: str = Field(..., min_length=1)

    @field_validator("amount", mode="after")
    @classmethod
    def check_amount(cls, v: float) -> float:
        val = validate_positive_amount(v, type('Info', (), {'field_name': 'amount'})())
        if val is None:
            raise ValueError("Amount cannot be null")
        return val


class CaseReportRecord(BaseIngestionRecord):
    report_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
