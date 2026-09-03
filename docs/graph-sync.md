# Graph Synchronization Strategy

The system relies on PostgreSQL as the primary source of truth for auditable investigation records, and Neo4j as the specialized engine for network analysis and visualization.

## Graceful Offline Degradation
If Neo4j goes offline:
1. The API remains fully functional for standard CRUD operations.
2. Ingestion jobs succeed in writing to PostgreSQL.
3. The graph sync status on affected `ExtractedEntity` and `ExtractedRelationship` rows is set to `RETRYABLE_FAILURE`.
4. A warning is surfaced to the user.

## Explicit Syncing
Synchronization to Neo4j is **explicitly managed** via the `IngestionService` and `GraphRepository`. We do not use automatic SQLAlchemy ORM hooks (e.g. `after_insert`) for syncing, as they obscure failures, complicate transactions, and hinder bulk-import performance.

## Status Tracking
Entities and relationships track their sync status:
- `PENDING`: Waiting to be synced.
- `SYNCED`: Successfully written to Neo4j.
- `RETRYABLE_FAILURE`: Network error or Neo4j offline. Can be safely retried.
- `PERMANENT_FAILURE`: Schema mismatch or invalid data that Neo4j rejected. Requires manual intervention.
- `NOT_APPLICABLE`: Records that do not need graph representation.

## Idempotent Retries
Failed syncs can be re-run safely because:
- Nodes use `MERGE (n:Entity {id: $id})`.
- Relationships use `MERGE (a)-[r:TYPE {id: $rel_id}]->(b)` where `$rel_id` is a deterministic SHA-256 hash.
