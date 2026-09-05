# Operations Manual

This document outlines the operational procedures for managing the SIH synthetic demo system.

## Health Checks
The backend provides a unified health check endpoint:
- **Endpoint:** `GET /health`
- **Behavior:** Checks the status of the API, PostgreSQL connection, and Neo4j connection.
- **Usage:** Should be used by load balancers, Docker, or Kubernetes to monitor service health.

## Database Migrations
We use robust migration tools to manage schema changes.
- **PostgreSQL:** Managed via Alembic. Run `alembic upgrade head` to apply new migrations.
- **Neo4j:** Graph schemas (constraints, indexes) are applied via startup scripts within the FastAPI application lifecycle.

## Logging
- The application logs to standard output (stdout) and standard error (stderr).
- Log levels can be configured via environment variables.
- Logs include timestamps, log levels, and request context. For security, sensitive data (like passwords or tokens) is scrubbed from logs.

## Safe Failure
The application is designed with safe failure mechanisms:
- If Neo4j is temporarily down, the application will not crash. API calls requiring graph data will return a structured 503 Service Unavailable error, while relational data remains accessible.
- Global exception handlers catch unhandled errors and return generic 500 errors to the client, preventing the leakage of stack traces or sensitive system information.

## Backups (Demo Context)
As this is a synthetic demo environment, data persistence is not critical. However, scripts are provided to load base synthetic data sets if the databases need to be rebuilt.
