# Deployment Readiness

**CRITICAL NOTICE:** This system is built and deployed exclusively as a **synthetic-demo only system**. It is not intended, nor approved, for production deployment with real law enforcement, financial, or personally identifiable data.

## Deployment Architecture

The application is designed to be deployed using containerization (Docker) to ensure consistency across environments.

- **Frontend:** Next.js application, served statically or via Node.js.
- **Backend:** FastAPI application running on Uvicorn/Gunicorn.
- **Databases:** Managed instances of PostgreSQL and Neo4j.

## Security and Secrets Management

- **No Real Secrets in Source Control:** The codebase does not contain any hardcoded API keys, database passwords, or secret tokens.
- **Environment Variables:** All configuration is managed via environment variables. An `.env.example` file is provided to document required variables without exposing actual secrets.

## Operations and Resilience

- **Health Checks:** The FastAPI backend exposes a `/health` endpoint that verifies connectivity to both PostgreSQL and Neo4j. Load balancers and container orchestrators should use this endpoint.
- **Failure Behavior:** The system is designed to fail safely. If a downstream service (like Neo4j) is unavailable, the API will return structured error responses rather than crashing, and the frontend will display graceful degradation messages.
- **Backups:** For demo purposes, synthetic database snapshots are used. In a hypothetical production environment, automated point-in-time recovery (PITR) backups for both PostgreSQL and Neo4j would be mandatory.
