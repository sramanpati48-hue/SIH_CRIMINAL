# Extraction Pipeline

The SIH-CRIMINAL extraction pipeline processes raw case reports into structured entities and relationships, mapping unstructured text into a graph-ready format.

## Overview

1. **Input**: A `Document` record in PostgreSQL containing raw text (`raw_content`).
2. **Provider**: An implementation of `ExtractorProvider` (e.g., `MockExtractor`, or eventually an LLM/NLP model) processes the text.
3. **Extraction**:
   - Entities (e.g., PERSON, PHONE, VEHICLE, LOCATION) are extracted with confidence scores and offsets.
   - Relationships (e.g., CALLED, INVOLVED_IN) link extracted entities.
4. **Persistence**: Extracted items are stored in PostgreSQL as `ExtractedEntity` and `ExtractedRelationship` with an initial `UNREVIEWED` status.
5. **Graph Sync**: Entities and relationships that reach an `ACCEPTED` or `CORRECTED` status are subsequently synced to the Neo4j graph database.

## Design Constraints

* **Idempotency**: Processing the same document multiple times will not create duplicate `UNREVIEWED` records. Existing records that have already been reviewed will not be overwritten by subsequent extractions.
* **Traceability**: All extractions retain their `original_value`, `start_offset`, and `end_offset` to anchor them to the source document for explainability.
* **Auditability**: Every change (extraction or human review) generates an `AuditLog` entry.

## Error Handling

* If Neo4j is offline, PostgreSQL remains the source of truth, and the pipeline marks graph synchronization as a `RETRYABLE_FAILURE`.
