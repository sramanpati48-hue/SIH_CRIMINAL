# Neo4j Development Guide

## Overview
This document covers local development, testing, and offline behaviors for the Neo4j graph subsystem in the SIH 26189 Prototype.

## Graceful Offline Degradation
The backend is designed to run seamlessly **without** Neo4j for developers who do not have Docker or a local database available.
- `GET /api/v1/health`: Returns 200 OK.
- `GET /api/v1/graph/health`: Returns 200 OK with `status: "unavailable"`.
- PostgreSQL routes (`/cases`, `/documents`) function normally.
- Graph data endpoints (`/cases/{id}/graph`, etc.) return `503 Service Unavailable` with a clear message.
- The system automatically suppresses Neo4j connection retries and excessive error logging.

## Local Docker Setup (Optional)
If you have Docker available locally, you can start PostgreSQL and Neo4j using the provided Compose file:

```bash
docker-compose up -d
```

### Environment Variables
Configure your `.env` or `apps/backend/.env` with safe development defaults:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_dev_password
NEO4J_DATABASE=neo4j
```
*Note: Never expose `NEO4J_PASSWORD` in logs, API responses, or commit it to source control.*

## Running Tests

### Standard Test Suite
The standard test suite isolates the offline behavior and mocks driver responses. It does not require Neo4j:
```bash
pytest -q tests/backend/
```

### Integration Tests
To run tests against a live Neo4j database, the integration suite uses the `@pytest.mark.neo4j` marker.
These tests automatically skip if `NEO4J_URI` is unreachable.
```bash
pytest -m neo4j
```

## Current Limitations
- **No Background Sync**: Currently, creating a document in PostgreSQL does not automatically trigger graph extraction/syncing. The service boundaries are explicitly separated to support future asynchronous worker implementation.
- **Development-Only API Endpoints**: The endpoints under `/api/v1/graph`, `/api/v1/cases/{id}/graph`, etc., do not enforce authorization yet and are intended for development/prototype demonstration.
- **Constraints**: Relationship uniqueness constraints are only fully supported natively in Neo4j Enterprise Edition; the application degrades gracefully to ID checks during MERGE.
