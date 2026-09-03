# Risks, Assumptions, & Security Requirements
## SIH 26189: AI-Powered Criminal Network Analysis System (Prototype)

---

## 1. Security Requirements
Even as a prototype, the system must demonstrate awareness of law enforcement security standards:
- **No Secrets in Source:** Use `.env` files for DB credentials. Never commit them.
- **Authentication:** The prototype should mock RBAC (Analyst vs. Admin) to demonstrate secure access to verification workflows.
- **Auditability:** Every human intervention (Accept/Reject) MUST be logged with a rationale and a timestamp.

## 2. Testing Strategy
To maintain a stable SIH prototype, the testing strategy is strictly scoped:
- **Backend:** Pytest for Pydantic schema validation and FastAPI endpoint status codes.
- **Frontend:** TypeScript strict mode enforcement (`tsc --noEmit`).
- **Integration:** A dedicated script to verify that Neo4j node counts match PostgreSQL `extracted_entities` counts.

## 3. Risks & Prototype Mitigations
| Risk | Mitigation |
| :--- | :--- |
| **NLP Over-extraction (Noise):** The NLP model extracts too many useless connections. | Use high confidence thresholds for the MVP and allow human reviewers to easily filter or reject edges in the UI. |
| **Graph Visual Clutter:** Cytoscape rendering becomes laggy with too many nodes. | Scope the synthetic dataset for the demo to <100 nodes/edges to clearly demonstrate capabilities without overwhelming the browser. |
| **Scope Creep (Productionizing too early):** Wasting time on Kafka or Spark. | Stick strictly to the lightweight Python/FastAPI/Postgres/Neo4j stack outlined in the architecture. |
