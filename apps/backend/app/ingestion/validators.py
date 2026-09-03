"""Custom Pydantic validators for ingestion schemas."""

from typing import Any
from pydantic import ValidationInfo

def validate_positive_amount(v: float | None, info: ValidationInfo) -> float | None:
    if v is not None and v <= 0:
        raise ValueError("Amount must be strictly positive.")
    return v

def validate_non_empty_string(v: str, info: ValidationInfo) -> str:
    if not v or not str(v).strip():
        raise ValueError(f"{info.field_name} cannot be empty.")
    return v
