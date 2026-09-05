# Case Access Control

To enforce strict isolation of sensitive investigative evidence, the system applies explicit case-level access controls via the `CaseAccess` mapping table. 

## Hierarchy of Access
The system defines four hierarchical access levels (`CaseAccessLevel` enum):
1. **MANAGE**: Full control over the case, including updating details, adding evidence, and (if permitted by role) changing access assignments. (Includes REVIEW, ANALYZE, VIEW).
2. **REVIEW**: Permission to accept/reject NLP-extracted entities and relationships. (Includes ANALYZE, VIEW).
3. **ANALYZE**: Permission to run graph analytics, pattern detection, and similarity searches. (Includes VIEW).
4. **VIEW**: Read-only access to case details and visualization. (Includes VIEW only).

## Rules & Constraints
- **Implicit Assignments:** When an Investigator creates a new case, they are automatically granted `MANAGE` access to it.
- **Global Admins:** Administrators automatically bypass specific case assignment checks, retaining global access.
- **Strict Isolation:** Non-administrative users attempting to view, analyze, or modify a case they are not explicitly assigned to will receive a `403 Forbidden` error. Case listings are also filtered to only show permitted cases, preventing metadata leakage.
- **Assignment Control:** Only Administrators (or users with specific MANAGE privileges) can grant, modify, or revoke case access for other users. Users cannot self-assign access to cases.
- **Revocation:** If an assignment is revoked (`is_active=False`), the user immediately loses access to the case.
