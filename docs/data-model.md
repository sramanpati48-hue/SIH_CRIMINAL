# Data Model Document
## SIH 26189: AI-Powered Criminal Network Analysis System (Prototype)

---

## 1. PostgreSQL Schema (Relational State & Audit)
PostgreSQL serves as the system of record for application state and human-in-the-loop audit logs.

- **`users`:** `id`, `username`, `role` (Analyst, Admin).
- **`cases`:** `id`, `case_name`, `description`.
- **`evidence_files`:** `id`, `case_id`, `filename`, `content` (for mapping text snippets).
- **`extracted_entities`:** `id`, `type` (Person, Phone, etc.), `name`, `confidence`, `verification_status`.
- **`extracted_relationships`:** `id`, `source_entity_id`, `target_entity_id`, `relation_type`, `evidence_id`, `snippet`, `confidence`, `verification_status`.
- **`audit_logs`:** `id`, `action` (e.g., REJECT_RELATION), `target_id`, `rationale`, `user_id`, `timestamp`. (Crucial for SIH prototype explainability).

## 2. Neo4j Graph Schema (Network & Patterns)
Neo4j serves as the operational graph for visualization and analytics. It is strictly kept in sync with the `extracted_relationships` table.

- **Nodes:** 
  - `:Person` (name, status)
  - `:PhoneNumber` (number, status)
  - `:Account` (account_id, status)
  - `:Location` (address, status)
  - `:Vehicle` (plate, status)
- **Edges (Relationships):** 
  - `:CALLS` (duration, timestamp, evidence_id, status)
  - `:TRANSFERS` (amount, timestamp, evidence_id, status)
  - `:OWNS` (evidence_id, status)
  - `:LOCATED_AT` (evidence_id, status)
