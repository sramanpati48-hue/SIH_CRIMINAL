# Report Export Security

Exporting case data inherently moves data out of the system's active security boundary. The system implements strict countermeasures to ensure report generation itself does not introduce vulnerabilities.

## 1. Authentication and Authorization
- **Endpoint Check:** `GET /cases/{case_id}/report/html` depends on `require_case_access(CaseAccessLevel.VIEW)`.
- Users cannot enumerate or export reports for cases they are not explicitly assigned to (unless they are an Administrator).
- Authentication uses the short-lived in-memory JWT. Unauthenticated requests return `401`.

## 2. Injection Prevention (Jinja2)
- **Autoescaping:** The report uses `jinja2.Environment(autoescape=select_autoescape(['html']))`.
- **No `|safe`:** The `|safe` filter is strictly banned in the template. All text (e.g. case titles, descriptions, evidence snippets, alert explanations) is HTML-escaped.
- **Server-Generated Template Path:** The template path is hardcoded (`report_template.html`). User input never dictates the path (mitigating Local File Inclusion).

## 3. Safe Filenames and Headers
- The downloaded filename is server-generated (`case-report-{case_id}.html`) and does not use potentially malicious user-provided case titles.
- **Security Headers:**
  - `Content-Type: text/html; charset=utf-8`
  - `Content-Disposition: attachment; filename="..."`
  - `X-Content-Type-Options: nosniff`
  - `Cache-Control: no-store`

## 4. Content Security Policy (CSP)
Downloaded HTML files could be opened in a browser context. A restrictive CSP is hardcoded in the `<meta>` tag of the report template:
`<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">`
- Disallows all external scripts, iframes, images, forms, and network connections.

## 5. Audit Logging
- Exactly one `REPORT_EXPORTED` audit log is created per successful download.
- If an error occurs, no template paths or stack traces are logged.
- The audit record payload stores only metadata (counts, timestamps). HTML output, passwords, or raw evidence are never stored in the audit trail.
