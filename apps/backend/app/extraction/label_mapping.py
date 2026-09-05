"""Mapping external provider labels to internal entity types."""

SPACY_TO_INTERNAL = {
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "GPE": "LOCATION",
    "LOC": "LOCATION",
    "FAC": "LOCATION",
    "DATE": "DATE",
    "TIME": "DATE",
    "MONEY": "MONEY",
    "QUANTITY": "MONEY",
    "PRODUCT": "VEHICLE",
}

def map_spacy_label(label: str) -> str | None:
    """Map a spaCy label to an internal entity type, or None if unmapped."""
    return SPACY_TO_INTERNAL.get(label)
