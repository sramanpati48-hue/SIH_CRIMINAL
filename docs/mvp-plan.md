# MVP Implementation Plan
## SIH 26189: AI-Powered Criminal Network Analysis System (Prototype)

---

## 1. Practical MVP Roadmap

To ensure a working, impressive prototype for the SIH presentation, development is staged into 5 practical phases.

### Phase 1: Core Schemas & Synthetic Data
- Define Pydantic models.
- Set up PostgreSQL (SQLModel/SQLAlchemy) and Neo4j connections.
- **Key Output:** Python script generating a synthetic dataset of 5-10 interconnected entities (Burner phone ring or financial laundering cycle).

### Phase 2: Lightweight NLP Extraction
- Implement a basic Spacy NER pipeline and Regex matchers for the synthetic dataset.
- Extract nodes and edges with confidence scores and source text snippets.
- **Key Output:** Extraction engine that parses text/CSV and outputs JSON candidates.

### Phase 3: DB Integration & Graph Analytics
- Save candidates to Postgres.
- Sync validated structures to Neo4j.
- Implement Cypher queries for basic analytics (Degree centrality, loop detection).
- **Key Output:** Back-end pipeline successfully building the dual-database state.

### Phase 4: API & Human Verification
- Build FastAPI endpoints for ingestion, graph retrieval, and verification.
- Implement the audit logging mechanism for Accepted/Rejected edges.
- **Key Output:** Functional REST API with Swagger documentation.

### Phase 5: Interactive UI (Frontend)
- Build TypeScript React app.
- Render graph using Cytoscape.js.
- Create an "Evidence Panel" that shows the text snippet when an edge is clicked, allowing the user to Accept/Reject.
- **Key Output:** End-to-End polished prototype ready for demonstration.
