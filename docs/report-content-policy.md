# Report Content Policy

The generated case reports strictly govern what data is exported to ensure safety, relevance, and analytical integrity.

## Inclusion Policy
- **Case Metadata:** Number, title, status, priority, creation timestamp.
- **Entities:** Only those with `verification_status` in `ACCEPTED` or `CORRECTED`.
- **Relationships:** Only those with `verification_status` in `ACCEPTED` or `CORRECTED`.
- **Alerts/Patterns:** Handled via the alert lifecycle (currently OPEN or ACCEPTED).

## Exclusion Policy
- **Unverified Data:** Any entity or relationship marked `UNREVIEWED` or `REJECTED` is categorically excluded from the report. They are treated as unreliable hypotheses.
- **Full Source Documents:** Only brief excerpts are included to provide context. The full document is not exported to limit data sprawl and cognitive overload.
- **Predictive Guilt:** AI predictions about guilt or criminal propensity are fundamentally omitted.

## Bounded Evidence Policy
To prevent data leaks and maintain report readability:
- `REPORT_MAX_EVIDENCE_CHARS = 500`: Excerpts are truncated deterministically with an ellipsis.
- `REPORT_MAX_ENTITIES = 500`: Maximum rows in the entities table.
- `REPORT_MAX_RELATIONSHIPS = 500`: Maximum rows in the relationships table.
- `REPORT_MAX_ALERTS = 200`: Maximum alerts included.

## Neutral Language and Disclaimers
A mandatory disclaimer appears at the top of every generated report:
> "IMPORTANT DISCLAIMER: This is a prototype system running on synthetic data. All extracted entities, relationships, and alerts require human verification. This report provides investigative context and does not establish guilt, criminal probability, or confirmed wrongdoing."
