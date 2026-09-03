# API Design Document
## SIH 26189: AI-Powered Criminal Network Analysis System (Prototype)

---

## 1. API Endpoints (FastAPI)
To keep the prototype practical, the API is scoped to the minimum required endpoints for ingestion, graph rendering, and verification.

### 1.1 Ingestion & Extraction
- **`POST /api/cases/{case_id}/ingest`**
  - **Payload:** UploadFile (txt, csv, json)
  - **Action:** Triggers NLP extraction pipeline.
  - **Response:** Extracted candidate entities and relationships (`status: PENDING`).

### 1.2 Graph Visualization
- **`GET /api/cases/{case_id}/graph`**
  - **Query:** `include_rejected` (bool)
  - **Response:** JSON arrays of `nodes` and `edges` formatted for Cytoscape.js.

### 1.3 Human Verification Workflow
- **`POST /api/relations/{relation_id}/verify`**
  - **Payload:** `{"action": "ACCEPT" | "REJECT" | "CORRECT", "rationale": "Matches CDR log"}`
  - **Action:** Updates Postgres, syncs to Neo4j, writes to `audit_logs`.

### 1.4 Graph Analytics
- **`GET /api/cases/{case_id}/analytics/financial-loops`**
  - **Action:** Runs a Cypher query in Neo4j to find A->B->C->A transaction cycles.
  - **Response:** List of cycles with nodes and total amounts.
