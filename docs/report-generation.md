# Report Generation (Milestone 13)

The AI-Assisted Criminal Network Analysis System generates on-demand HTML reports for specific cases. These reports provide a safe, untempered snapshot of human-verified findings.

## Design Philosophy

- **On-Demand:** Reports are generated entirely in memory upon request. No static HTML files are stored on disk, reducing the attack surface.
- **Evidence-Backed:** All relationships included in the report feature the explicit bounded text snippet that forms the basis of the relationship, allowing reviewers to verify the AI's extraction against the source.
- **Accepted / Corrected Only:** The report omits all UNREVIEWED, REJECTED, and NEEDS_MORE_INFORMATION entities and relationships to ensure that hypotheses are not presented as fact.
- **Neutral Formatting:** Reports avoid accusatory language, utilizing words like "investigative support", "alerts", and "patterns".

## Process Flow

1. An authenticated user (Investigator/Admin) with case VIEW access initiates the export via the frontend UI.
2. The `GET /cases/{case_id}/report/html` backend route validates the JWT and RBAC.
3. The `ReportService` queries the database for:
   - Case metadata
   - ExtractedEntities (ACCEPTED or CORRECTED)
   - ExtractedRelationships (ACCEPTED or CORRECTED)
   - Alerts (OPEN or ACCEPTED)
4. Data is mapped to schemas (e.g., `ReportEntityItem`) and limits are applied (e.g. `REPORT_MAX_EVIDENCE_CHARS = 500`).
5. A single Jinja2 HTML template (`report_template.html`) is rendered safely with `autoescape=True`.
6. A single `REPORT_EXPORTED` event is logged in the append-only `audit_logs` table.
7. The HTML response is returned with secure headers (`Content-Disposition: attachment`, `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`).

## UI Integration
The frontend utilizes `window.URL.createObjectURL` to download the Blob response and immediately revokes it to prevent persistence in browser storage.
