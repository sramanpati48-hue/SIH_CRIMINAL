# System Architecture Document
## SIH 26189: AI-Powered Criminal Network Analysis System (Prototype)

---

## 1. Component Architecture
For a practical SIH MVP, the system uses a modular, lightweight monolithic architecture to reduce deployment complexity while maintaining strict service boundaries.

- **Frontend:** TypeScript + React (Strict Mode) using Cytoscape.js for graph rendering.
- **Backend API:** Python + FastAPI with Pydantic for validation.
- **Relational Storage:** PostgreSQL for application state, verification status, and audit logging.
- **Graph Storage:** Neo4j for nodes, edges, and network path traversal.

## 2. AI & Analytics Responsibilities

### 2.1 NLP Responsibilities (Natural Language Processing)
- **Task:** Process unstructured synthetic police reports.
- **Scope:** Extract Entities (Named Entity Recognition for People, Locations, Organizations) and Relationships (Rule-based or lightweight LLM parsing to link entities).
- **Prototype Approach:** Use lightweight Spacy NER pipelines and Regex for structured IDs (phone numbers, accounts) to ensure fast, deterministic extraction without requiring massive GPU resources.

### 2.2 ML Responsibilities (Machine Learning)
- **Task:** Entity Resolution and Confidence Scoring.
- **Scope:** Assign a confidence score (0.0 - 1.0) to extracted relationships based on source text proximity. Assist in deduplicating aliases (e.g., matching "J. Doe" to "John Doe" using fuzzy matching or simple embeddings).
- **Constraint:** ML is **strictly prohibited** from generating "guilt scores" or predictive criminal classifications.

### 2.3 Graph Analytics Responsibilities
- **Task:** Uncover structural network patterns.
- **Scope:** 
  - **Pathfinding:** Shortest path between two suspects.
  - **Pattern Detection:** Identify financial loops (A -> B -> C -> A) indicating money laundering patterns.
  - **Centrality:** Calculate Degree Centrality to identify highly connected hubs (e.g., a central burner phone).

## 3. Data Flow
1. **Ingestion:** Analyst uploads a synthetic report via the Frontend.
2. **Extraction (NLP/ML):** FastAPI backend routes text to the NLP service. Entities, relationships, confidence scores, and source evidence snippets are extracted.
3. **Persistence:** Candidates are saved to PostgreSQL (`PENDING` status) and synced to Neo4j.
4. **Verification:** Analyst reviews the graph, clicks a link, sees the evidence snippet, and clicks "Accept" or "Reject".
5. **Audit Sync:** FastAPI logs the action immutably in PostgreSQL and updates the edge status in Neo4j.
