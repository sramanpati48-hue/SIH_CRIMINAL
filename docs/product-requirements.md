# Product Requirements Document (PRD)
## SIH 26189: AI-Powered Criminal Network Analysis System (Prototype)

---

## 1. Problem Understanding
Law enforcement agencies handle massive volumes of heterogeneous data—call detail records (CDRs), financial transactions, location logs, and unstructured police reports. Investigators currently struggle to manually "connect the dots" across these disparate silos. There is a critical need for an automated system to extract, link, and visualize this data. However, AI in law enforcement must be **explainable and verifiable**. Black-box models that predict "guilt" are unacceptable. The solution must assist investigators by providing **investigative leads** supported by traceable evidence and human-in-the-loop oversight.

## 2. System Boundaries
**In-Scope (SIH Prototype):**
- Ingestion of synthetic structured data (CSV/JSON for CDRs, transactions) and unstructured text (reports).
- Automated extraction of entities (People, Phones, Accounts, Locations, etc.) and relationships.
- Dual-database storage (PostgreSQL for state/audit, Neo4j for network graphs).
- Interactive graph visualization with explainable evidence snippets.
- Human-in-the-loop verification (Accept/Reject/Correct) and audit logging.

**Out-of-Scope:**
- Real PII, real police data, or live integrations with law enforcement systems.
- Automated guilt calculation or predictive policing algorithms.
- Large-scale distributed processing (e.g., Kafka, Spark); the MVP will run as a practical, monolithic prototype.

## 3. User Roles
1. **Investigative Analyst:** Uploads synthetic case files, reviews AI-extracted leads, verifies relationships, and explores the interactive graph to find patterns.
2. **System Admin/Auditor:** Reviews immutable audit logs to ensure accountability and traces the rationale behind human verifications.

## 4. MVP Scope
For the SIH prototype, the MVP will focus on a **minimum working version** demonstrating the end-to-end pipeline:
1. Ingest a pre-defined set of synthetic text reports and CSV logs.
2. Extract entities and relationships using a lightweight NLP approach.
3. Render a practical, interactive UI graph showing nodes (People, Accounts) and edges (Calls, Transfers) with evidence tooltips.
4. Demonstrate the human verification workflow updating the Postgres state and Neo4j graph in sync.
