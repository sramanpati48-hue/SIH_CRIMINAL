# Architecture Summary

The AI-Assisted Criminal Network Analysis System employs a modern, decoupled architecture designed for scalability, explainability, and security.

## High-Level Components

### 1. Frontend: Next.js & React
- **Language:** TypeScript (Strict Mode)
- **Role:** Delivers the interactive user interface, including the network graph visualization, human-in-the-loop review screens, and analytics dashboards.
- **Features:** Client-side routing, state management, and strict type checking to ensure robust UI components.

### 2. Backend: FastAPI (Python)
- **Language:** Python 3.10+
- **Role:** The core API gateway and orchestration layer.
- **Features:** 
  - **Type Safety:** Explicit type hints and Pydantic models for request/response validation.
  - **Asynchronous:** High-performance async I/O.
  - **Modular Services:** Clear boundaries between data extraction, graph querying, and relational data management.
  - **Security:** Enforces Role-Based Access Control (RBAC) and uses parameterized SQL/Cypher queries to prevent injection attacks.

### 3. Relational Database: PostgreSQL
- **Role:** The primary source of truth for structured data.
- **Data Stored:** User accounts, roles, case metadata, audit logs, and raw text documents.
- **Integration:** Accessed via an ORM or async database driver with strict parameterization.

### 4. Graph Database: Neo4j
- **Role:** The specialized engine for network analysis.
- **Data Stored:** Extracted entities (nodes) and their relationships (edges).
- **Features:** Enables rapid traversal of connections, pattern recognition, and similarity searches that would be computationally prohibitive in a purely relational model.

## Data Flow
1. Unstructured synthetic text is uploaded to the backend and stored in PostgreSQL.
2. The NLP pipeline extracts entities and relationships.
3. Extracted data is presented to the user via Next.js for **Human-in-the-Loop** verification.
4. Verified connections are stored in Neo4j with full traceability (source text, confidence score, timestamps).
5. The Next.js frontend queries FastAPI, which aggregates data from both PostgreSQL and Neo4j to render the network graph and reports.
