# Graph Schema Reference

## Overview
This document defines the strictly controlled graph schema for the SIH 26189 prototype. 

To support both specific node matching (e.g., `MATCH (p:Person)`) and generic traversal (e.g., `MATCH (e:Entity)`), all extracted domain entities are assigned a specific label AND the generic `Entity` label. System nodes (`Case`, `Document`, `Event`) do not use the `Entity` label.

## Node Labels

### System Nodes
| Label | Stable ID Property | Description |
| :--- | :--- | :--- |
| `Case` | `case_id` | Represents an investigation case. |
| `Document` | `document_id` | Represents uploaded evidence. |
| `Event` | `event_id` | Represents a specific incident or timeline event. |

### Domain Entities (Also labeled as `:Entity`)
| Specific Label | Stable ID Property | Description |
| :--- | :--- | :--- |
| `Person` | `person_id` | A suspect, witness, or person of interest. |
| `Phone` | `phone_id` | A phone number. |
| `Vehicle` | `vehicle_id` | A vehicle plate/registration. |
| `Location` | `location_id` | A physical address or coordinate. |
| `Organization` | `organization_id` | A company or criminal group. |
| `BankAccount` | `account_id` | A financial account number. |

### Common Node Properties
All nodes created through the API include:
- `case_id`: The ID of the originating case.
- `created_at`: Node creation timestamp.

---

## Relationship Types

### Allowed Types
| Type | Typical Usage |
| :--- | :--- |
| `CALLED` | `(Phone)-[:CALLED]->(Phone)` |
| `USED` | `(Person)-[:USED]->(Phone)` |
| `OWNS` | `(Person)-[:OWNS]->(Vehicle)` |
| `VISITED` | `(Person)-[:VISITED]->(Location)` |
| `TRANSFERRED_TO` | `(BankAccount)-[:TRANSFERRED_TO]->(BankAccount)` |
| `INVOLVED_IN` | `(Person)-[:INVOLVED_IN]->(Event)` |
| `MENTIONED_IN` | `(Entity)-[:MENTIONED_IN]->(Document)` |
| `CONNECTED_TO` | Generic fallback or known association |
| `OCCURRED_AT` | `(Event)-[:OCCURRED_AT]->(Location)` |

### Relationship Evidence Properties
Every relationship must include evidence properties for human-in-the-loop verification:
- `relationship_id` (String): A deterministic hash (`SHA-256`) of source_id, type, target_id, document_id, event_date.
- `source_document_id` (String): Originating document ID.
- `source_type` (String): e.g., 'CDR', 'REPORT'.
- `event_date` (DateTime): When the event occurred (if applicable).
- `confidence` (Float 0.0-1.0): Extraction/resolution confidence.
- `verified` (Boolean): Whether human-reviewed.
- `evidence_text` (String): Snippet of the original text.

---

## Uniqueness Constraints
Stable ID uniqueness is enforced via constraints on initialization (e.g., `CREATE CONSTRAINT FOR (p:Person) REQUIRE p.person_id IS UNIQUE`). Constraint syntax is compatible with Neo4j Community Edition for node constraints. 
