# Relationship Rules

The system extracts relationships using explicit, deterministic Python rules in `apps/backend/app/extraction/relationship_rules.py`.

## Supported Types

The following types are allow-listed and strictly enforced by Pydantic schemas:
- `CALLED`
- `USED`
- `OWNS`
- `VISITED`
- `TRANSFERRED_TO`
- `INVOLVED_IN`
- `MENTIONED_IN`
- `CONNECTED_TO`
- `OCCURRED_AT`

Any other type will result in a schema validation error.

## Rule Patterns

Relationships are *only* created when explicit evidence exists.

### CALLED
- Connects `PERSON` to `PERSON` (or `PHONE`).
- **Patterns**: "called", "contacted by phone", "spoke with".
- *Prohibited*: Inferring a call simply because two people occur in the same sentence.

### USED
- Connects `PERSON` to `VEHICLE` or `PHONE`.
- **Patterns**: "used", "travelled in".

### OWNS
- Connects `PERSON` to `VEHICLE` or `BANK_ACCOUNT`.
- **Patterns**: "owns", "owned", "is the owner of".

### VISITED
- Connects `PERSON` to `LOCATION`.
- **Patterns**: "visited", "was seen at", "travelled to".

### TRANSFERRED_TO
- Connects `PERSON` or `BANK_ACCOUNT` to `PERSON` or `BANK_ACCOUNT`.
- **Patterns**: "transferred to", "sent to".
- *Prohibited*: Inferring financial intent or crime; uses strictly neutral transaction terms.

### INVOLVED_IN
- Connects `PERSON` to `CASE_ID`.
- **Patterns**: "is mentioned in", "is linked to", "is involved in".

### CONNECTED_TO
- General connection between entities, often `ORGANIZATION`s.
- **Patterns**: "is connected to", "has a connection with".
- *Prohibited*: Creating connections based merely on proximity.

### OCCURRED_AT
- Connects `CASE_ID` to `LOCATION`.
- **Patterns**: "occurred at", "happened in", "took place at".

## Ambiguity Handling

If an exact relationship boundary cannot be resolved, or if multiple entities overlap identically, the system prefers skipping the relationship creation or returning a structured warning rather than inventing an unsupported relationship. The human-in-the-loop review ensures that extracted candidates are factual.
