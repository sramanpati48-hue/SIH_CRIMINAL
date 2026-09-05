# Human Review Workflow

Given the sensitive nature of criminal network analysis, the system requires a **Human-in-the-Loop (HITL)** process for all extracted entities and relationships before they can be considered actionable intelligence or synced to the graph database.

## Review Statuses

Every extracted candidate has a `verification_status` mapped to one of the following:

- `UNREVIEWED`: The initial state of an extraction. Not synced to Neo4j.
- `ACCEPTED`: A human analyst has verified the extraction is correct. Synced to Neo4j.
- `REJECTED`: A human analyst has determined the extraction is a false positive. Not synced to Neo4j.
- `CORRECTED`: A human analyst has fixed the extraction (e.g., resolving a typo, canonicalizing a name). Synced to Neo4j.
- `NEEDS_MORE_INFORMATION`: The extraction requires further manual investigation or additional data sources before a decision can be made.

## Traceability & Immutability

When a human analyst changes the status of a candidate (especially to `CORRECTED`), the original output from the extraction model is **never** destructively overwritten.
Instead, the correction is applied to `canonical_name` (or similar fields), while `original_value`, `start_offset`, and `end_offset` remain intact.

## Audit Logs

All review decisions must include a rationale and the identity of the reviewer. This action is permanently recorded in the `AuditLog` table.
