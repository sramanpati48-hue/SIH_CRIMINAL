# Authentication Architecture

This prototype implements authentication using JSON Web Tokens (JWT) signed with the HS256 algorithm.

## JWT Implementation
Access tokens are short-lived. Refresh tokens are intentionally excluded from this prototype as their secure rotation requires complexity out of scope for the current milestone.

**JWT Constraints:**
- **Signature Algorithm:** Exclusively `HS256`. The backend rejects `none` or other algorithms.
- **Payload Validation:** Standard claims `exp` (expiration), `sub` (subject), and optionally `jti` (JWT ID), `iss` (issuer), and `aud` (audience).
- **Timezones:** Expirations are evaluated using strict UTC times.

## Password Policy
Passwords are treated with care and adhere to OWASP recommendations:
- **Hashing:** We use raw `bcrypt` rather than a wrapper like `passlib` to avoid known wrapper bugs related to password length validation.
- **Maximum Length:** Bcrypt silently truncates or wraps passwords longer than 72 bytes. Therefore, the system explicitly **rejects any password input exceeding 72 UTF-8 bytes** before hashing.
- **Minimum Length:** Passwords must be at least 8 characters.
- **Work Factor:** Bcrypt cost is configurable (defaulting to 12).
- **Secret Constraints:** Passwords and password hashes are never logged and are explicitly omitted from all API responses and audit trails.

## User Session Validations
Beyond token validity, authorization dependencies verify that the user associated with the `sub` claim exists in the database and remains `active`. If a user is deactivated, any existing tokens immediately fail authorization checks.

## Frontend Token Handling
- Tokens are retained strictly in React memory state (`memoryToken`).
- Tokens are explicitly **not** written to `localStorage` or `sessionStorage`. This reduces persistent browser storage exposure but does not replace broader XSS protection mechanisms.
- On explicit logout or upon receiving a `401 Unauthorized` response from any API, the frontend immediately clears the in-memory token and redirects to the login screen.
