"""Extraction normalization utilities."""
import re
from datetime import datetime

def normalize_entity_value(entity_type: str, original_value: str) -> str:
    """Normalize extracted entity value based on its type."""
    val = original_value.strip()
    if not val:
        return val

    if entity_type == "PERSON":
        return " ".join([word.capitalize() for word in val.split()])
    elif entity_type == "PHONE":
        # Keep only digits and plus
        cleaned = re.sub(r"[^\d+]", "", val)
        if not cleaned.startswith("+") and len(cleaned) == 10:
            return f"+1{cleaned}"
        return cleaned
    elif entity_type == "DATE":
        try:
            # Try basic ISO format parsing
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.isoformat()
        except Exception:
            return val
    elif entity_type == "BANK_ACCOUNT":
        return re.sub(r"[^\w]", "", val).upper()
    elif entity_type == "VEHICLE":
        return re.sub(r"[^\w]", "", val).upper()
    elif entity_type in ["ORGANIZATION", "LOCATION", "ALIAS"]:
        return val.upper()
    
    return val
