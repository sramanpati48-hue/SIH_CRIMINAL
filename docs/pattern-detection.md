# Pattern Detection and Alerts

The pattern detection subsystem automatically flags suspicious investigative leads. **Important:** These are leads, not assertions of guilt.

## Detectors

Detectors are deterministic algorithms implemented as subclasses of `PatternDetector`. 

### 1. Shared Phone / Vehicle / Location
- **Trigger:** Multiple distinct `PERSON` or `ACCOUNT` entities sharing a common `PHONE`, `VEHICLE`, or `LOCATION` node.
- **Why:** Indicates potential burner phones, safehouses, or shared operational vehicles.

### 2. Cross-Case Connector
- **Trigger:** A node appearing in more than one unique `case_id`.
- **Why:** Highlights serial behavior or organized rings spanning multiple seemingly unrelated investigations.

### 3. Rapid Transaction Chain
- **Trigger:** An entity (usually `BANK_ACCOUNT`) that acts as a pass-through (both receives and sends) in a chain of at least 3 transactions.
- **Why:** Classic indicator of money laundering (layering).

### 4. High Connectivity (Hub)
- **Trigger:** Node PageRank score falls in the top 5% of the subgraph.
- **Why:** Central figures or organizers.

### 5. Bridge Between Communities
- **Trigger:** Node Betweenness Centrality > 0.3.
- **Why:** Identifies couriers, money mules, or intermediaries connecting distinct operational cells.

## Alert Structure
Alerts have:
- `alert_type`: The pattern detected.
- `severity`: LOW, MEDIUM, HIGH, CRITICAL.
- `confidence_score`: 0.0 - 1.0 (How reliable the evidence is).
- `evidence_ids`: Link back to `documents` for full traceability.
- `status`: Tracks the human-in-the-loop review state.
