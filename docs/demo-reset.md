# Demo Reset Mechanism

To facilitate repeatable demonstrations and ensure clean state, the system includes a cross-platform demo reset mechanism.

## Purpose
The reset mechanism wipes all current data and reloads the baseline synthetic data set (e.g., the `CASE-2024-SYN-001` scenario).

## Safety Controls
This script is highly destructive and is protected by strict environment variable checks:
- The reset mechanism will **ONLY** execute if the `APP_ENV` environment variable is explicitly set to `demo` or `development`.
- If `APP_ENV` is set to `production` or is undefined, the script will abort immediately and log a critical warning.

## How it Works
1. **Validation:** Checks `APP_ENV`.
2. **PostgreSQL Wipe:** Drops and recreates the relational schema, clearing all users, cases, and unstructured documents.
3. **Neo4j Wipe:** Executes a Cypher query (`MATCH (n) DETACH DELETE n`) to clear the entire graph database.
4. **Seed Data:** Re-runs the synthetic seed scripts to populate both databases with the baseline demo scenario.

## Usage
Run the script via the command line on the backend server:
```bash
python scripts/reset_demo_env.py
```
