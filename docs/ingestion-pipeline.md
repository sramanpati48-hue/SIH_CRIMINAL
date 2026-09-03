# Ingestion Pipeline

The SIH 26189 prototype ingestion pipeline is designed for robustness, memory efficiency, idempotency, and dual-persistence (PostgreSQL + Neo4j).

## Architecture
1. **Pydantic Validation**: All incoming data (CSV/JSON) is validated against strict Pydantic schemas (`apps/backend/app/ingestion/schemas.py`).
2. **Pure Normalization**: Names, phones, dates, and IDs are deterministically normalized while preserving original values.
3. **Memory-Conscious Streaming**: CSVs are read row-by-row using generators, preventing memory exhaustion on large datasets.
4. **Idempotent Dual-Write**:
   - The data is first persisted/updated in PostgreSQL.
   - It is then synchronized to Neo4j using `MERGE` statements and deterministic Relationship/Node IDs.
5. **Graceful Fallback**: If Neo4j is offline, PostgreSQL records are saved, and the graph sync is marked as `RETRYABLE_FAILURE`.

## Idempotency
- **PostgreSQL**: Records use a combination of `case_id`, `source_record_type`, and `source_record_id` as logical keys. Repeated ingestion updates existing records.
- **Neo4j Nodes**: Merged on `id`.
- **Neo4j Relationships**: Relationship IDs are deterministically generated via SHA-256 hashes of `(source, target, relation_type, document_id, event_date)`. This guarantees that ingesting the same call log twice will never duplicate the `CALLED` edge.

## Error Handling
- Row-level errors do not crash the batch job. Invalid rows are recorded in `rejected_rows`, and processing continues.
- Safe error summaries are preserved in the `ProcessingJob` tracker without leaking raw PII or secrets.
- `PERMANENT_FAILURE` is assigned to invalid schemas. `RETRYABLE_FAILURE` is used for transient Neo4j connectivity issues.
