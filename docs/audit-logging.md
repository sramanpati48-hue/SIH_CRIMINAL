# Audit Logging

In alignment with law enforcement evidence handling standards, this prototype implements immutable audit trails for sensitive system actions.

## Append-Only Immutability
Audit logs are strictly append-only:
- **No Mutation API Routes:** There are no `PATCH`, `PUT`, or `DELETE` endpoints for audit logs.
- **No Internal Mutation Methods:** The underlying repository logic contains no methods to update or delete audit records.
- **Admin Constraints:** Administrators can view the audit logs but are technically restricted from modifying them through the application interface.

## Logged Actions
The system automatically logs actions including (but not limited to):
- `LOGIN_SUCCEEDED` / `LOGIN_FAILED`
- `AUTHORIZATION_DENIED`
- `CASE_CREATED` / `CASE_UPDATED`
- `DOCUMENT_UPLOADED`
- `ACCESS_GRANTED` / `ACCESS_REVOKED`

## Sensitive Data Redaction
To protect system integrity and comply with OWASP recommendations:
- The logging service utilizes a robust redaction mechanism (`_sanitize_state`) before persisting payloads.
- Passwords, password hashes, raw JWTs, secret keys, full document texts, raw stack traces, and database connection strings are never recorded in audit logs.
- If a logging mechanism encounters an error, the operation is safely degraded without leaking internal state.
