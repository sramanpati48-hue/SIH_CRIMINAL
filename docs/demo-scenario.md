# Demo Scenario: Synthetic Syndicate

This document outlines the canonical demo scenario used to showcase the capabilities of the SIH platform. All data is strictly synthetic.

## Scenario Overview
- **Case ID:** `CASE-2024-SYN-001`
- **Narrative:** Investigators are analyzing unstructured reports regarding a synthetic organized crime group involved in fictional smuggling operations.

## Expected Data Points

### Demo Accounts
The following synthetic accounts are seeded for the demonstration. Their passwords are dynamically set via the `$env:DEMO_PASSWORD` environment variable during the seeding process (e.g., `demopassword123`).
- **Administrator:** `demo_admin`
- **Investigator:** `demo_investigator` (Assigned MANAGE access to the demo case)
- **Analyst:** `demo_analyst` (Assigned ANALYZE access)
- **Reviewer:** `demo_reviewer` (Assigned REVIEW access)

### Nodes (Entities)
- **Person:** John Doe (Fictional Suspect), Jane Smith (Fictional Associate)
- **Location:** 123 Fake Street, Springfield
- **Phone:** 555-0199
- **Organization:** Frontway Logistics (Fictional Company)

### Edges (Relationships)
- `[John Doe] - COMMUNICATED_WITH -> [555-0199]`
- `[Jane Smith] - OWNS -> [Frontway Logistics]`
- `[John Doe] - RESIDES_AT -> [123 Fake Street]`

## Demonstrated Features

1. **Extraction & HITL Review:**
   - The system extracts the relationship `[John Doe] - RESIDES_AT - [123 Fake Street]` from a synthetic surveillance report.
   - The demonstrator logs in and manually accepts this extraction, emphasizing the human-in-the-loop requirement.

2. **Graph Alerts & Patterns:**
   - The system flags that `555-0199` has been contacted by multiple distinct suspects.
   - **Important:** This is presented as an *investigative lead* requiring further verification, not a statement of guilt.

3. **Similarity & Analytics:**
   - A similarity search on "Frontway Logistics" reveals shared attributes (e.g., shared fictional addresses) with another synthetic entity in the database.

4. **RBAC Behavior:**
   - The demonstrator shows that an "Analyst" role can view the graph but cannot approve pending extractions, whereas the "Investigator" role can.

5. **Report Generation:**
   - An HTML report is generated detailing the source evidence and timestamps for the established connections, adhering to the accepted/corrected filter policy.
