# Milestone 12 Limitations

The current implementation provides a robust security baseline (JWT, strict RBAC, Case-level isolation, and immutable audit logging). However, as a prototype, several limitations exist compared to a production system:

1. **Synthetic Data Constraint:**
   The system strictly operates on synthetic data. Real personal, criminal, police, financial, phone, or address data must not be ingested.

2. **Guilt Prediction & Human Verification:**
   The system surfaces *investigative leads* and candidate patterns. It requires mandatory Human-in-the-Loop review and does not independently predict guilt.

3. **In-Memory JWT Storage:**
   Access tokens are retained in memory for the active browser session and are cleared on logout or expiry. While this eliminates persistent storage (localStorage) exposure, it is not a complete defense against advanced Cross-Site Scripting (XSS). A production implementation would ideally use secure, `HttpOnly`, `SameSite` cookies coupled with CSRF tokens.

4. **Lack of Refresh Tokens:**
   To maintain simplicity, token rotation via Refresh Tokens is omitted. Users will need to re-authenticate when their short-lived access tokens expire.

5. **Local Cryptographic Storage:**
   Secrets (like the JWT signing key) are managed via standard environment variables (`.env`) rather than a dedicated secrets manager (like HashiCorp Vault or AWS Secrets Manager).

6. **Audit Tampering Outside Application:**
   While the application API strictly prohibits audit log mutation, an administrator with raw database access could modify the SQL tables. A production system should stream audit logs to a specialized WORM (Write Once, Read Many) storage tier.
