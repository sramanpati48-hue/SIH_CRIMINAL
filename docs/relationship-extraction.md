# Relationship Extraction

This document explains the deterministic relationship-extraction stage. In Milestone 9, we explicitly decoupled relationship extraction from entity extraction to increase reliability and explainability.

## Architecture

Relationship extraction occurs *after* entities have been extracted, validated, and persisted. 

1. **Entity Extraction**: `DocumentExtractionService` persists entity candidates.
2. **Review**: Human reviewers optionally verify or correct entity candidates.
3. **Relationship Extraction**: `RelationshipExtractionService` consumes the validated entity candidates and applies explicit, deterministic matching rules on the source text.
4. **Review**: Extracted relationship candidates start as `UNREVIEWED` and must be validated.
5. **Graph Sync**: Only `ACCEPTED` or `CORRECTED` candidates are synchronized to Neo4j.

## API Endpoints

- `POST /api/v1/documents/{document_id}/extract-relationships`: Executes the deterministic rules and creates idempotently generated relationships.
- `GET /api/v1/documents/{document_id}/relationship-candidates`: Fetches the currently extracted candidates.
- `POST /api/v1/extraction-candidates/relationship/{candidate_id}/review`: Re-uses the existing review endpoint to ACCEPT, REJECT, or CORRECT the relationship.
- `POST /api/v1/documents/{document_id}/sync-approved-relationships`: Synchronizes to Neo4j.

## Confidence and Offsets

- All offsets are verified against `source_text`. If the text bounded by `start_offset` and `end_offset` does not equal `evidence_text`, the schema rejects the relationship.
- Confidence is purely rules-based:
  - `0.95`: Exact explicit relationship pattern (e.g., "called").
  - `0.85`: Strong pattern.
  - `0.70`: Incomplete or ambiguous.
- All candidates strictly begin as `UNREVIEWED`. Confidence scores do not bypass the review stage.

## Idempotency

Relationship IDs are generated deterministically via SHA-256 hash using the document ID, source entity ID, target entity ID, relation type, rule version, evidence text, and event date. Repeated execution on the same text with the same rule version will yield the same relationship ID and will not duplicate PostgreSQL rows.
