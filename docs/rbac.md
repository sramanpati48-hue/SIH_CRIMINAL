# Role-Based Access Control (RBAC)

The system enforces broad functional authorization through a strict User `Role` enum.

## Available Roles
1. **ADMINISTRATOR**: Has global system access, can manage all cases, assign cases to other users, and access sensitive areas like the Model Registry and Audit Logs.
2. **INVESTIGATOR**: Can create cases, upload documents, and manage cases they are explicitly assigned to.
3. **ANALYST**: Can view and analyze cases they are assigned to, trigger Graph Analytics, and run ML Predictions. Cannot upload raw evidence.
4. **REVIEWER**: Can review extracted entities and relationships (Human-in-the-Loop) on assigned cases, but cannot manage case boundaries or trigger intensive ML workloads.

## Implementation Details
- Backend endpoints are protected using the `require_role` FastAPI dependency.
- This dependency ensures that the authenticated user possesses the exact necessary role to perform the requested operation.
- Users who authenticate successfully but lack the requisite role are rejected with a `403 Forbidden` response.
- The UI conditionally renders navigation links and actionable components (buttons, upload forms) based on the user's role claim.
