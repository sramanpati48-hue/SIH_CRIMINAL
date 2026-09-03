"""Pure deterministic normalization functions for ingestion."""

import re
from datetime import datetime
from typing import Any

def normalize_string(val: Any) -> str:
    """Trim and collapse whitespace."""
    if val is None:
        return ""
    val_str = str(val)
    return re.sub(r'\s+', ' ', val_str).strip()

def normalize_name(name: str) -> str:
    """Normalize human names to title case with standardized spacing."""
    clean = normalize_string(name)
    return clean.title()

def normalize_phone(phone: str) -> str:
    """Extract digits and prepend '+' if applicable, forming pseudo-E164."""
    clean = normalize_string(phone)
    if not clean:
        return ""
    digits = re.sub(r'[^\d+]', '', clean)
    if not digits.startswith('+') and len(digits) > 0 and digits[0] != '0':
        # Just a naive normalization for synthetic data
        digits = '+' + digits.lstrip('+')
    return digits

def normalize_vehicle_id(plate: str) -> str:
    """Uppercase and remove spaces/hyphens for vehicle plates."""
    clean = normalize_string(plate)
    return re.sub(r'[\s-]', '', clean).upper()

def normalize_account_id(account: str) -> str:
    """Uppercase and trim."""
    return normalize_string(account).upper()

def normalize_date(date_str: str) -> datetime | None:
    """Convert ISO8601 string to datetime."""
    clean = normalize_string(date_str)
    if not clean:
        return None
    try:
        # Handling basic isoformat with or without Z
        clean = clean.replace('Z', '+00:00')
        return datetime.fromisoformat(clean)
    except ValueError:
        return None

def normalize_amount(amount: Any) -> float | None:
    """Convert amount to float."""
    try:
        return float(amount)
    except (ValueError, TypeError):
        return None
