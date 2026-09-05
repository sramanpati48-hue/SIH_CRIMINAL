# Relationship Review Workflow

Relationships extracted by the `RelationshipExtractionService` undergo human-in-the-loop review.

## Review States

All newly extracted relationships start in the `UNREVIEWED` state.
The graph synchronization step strictly ignores `UNREVIEWED` relationships.

A human reviewer can submit a decision to change the status to:
- `ACCEPTED`: The relationship is factually correct.
- `REJECTED`: The relationship is incorrect and must never be synced.
- `CORRECTED`: The relationship type was wrong and is now corrected.
- `NEEDS_MORE_INFORMATION`: Ambiguous text requiring external verification.

## Review Audit Log

Using the configured `DEV_REVIEWER_ID` (since authentication is not enabled yet), every review decision generates an immutable `AuditLog` entry in PostgreSQL. This guarantees traceability.

## Correction

If a relationship is marked `CORRECTED`, the reviewer must provide:
1. `corrected_value`: The new relationship type (e.g. changing `OWNS` to `USED`).
2. `rationale`: A human-readable reason for the correction.

The original extracted evidence text, offsets, and endpoints are preserved intact to allow auditing the performance of the extraction rules.

## Neo4j Synchronization

Once a relationship is `ACCEPTED` or `CORRECTED`:
- If both its source entity and target entity are already synced to Neo4j, the relationship itself is synced.
- If Neo4j is offline, the status becomes `RETRYABLE_FAILURE` and the data is safely preserved in PostgreSQL.
