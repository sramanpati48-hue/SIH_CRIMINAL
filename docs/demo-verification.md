# Demo Verification Script

The `verify_demo_ready.py` script is a crucial utility used to validate that the environment is correctly configured and ready for a demonstration.

## Purpose
Before presenting the system, this script ensures all necessary services are running, configurations are safe, and the synthetic data is loaded.

## Checks Performed

1. **Environment Check:**
   - Verifies that `APP_ENV` is set to `demo` or `development`. Warns if not.
   - Ensures no production secrets or real API keys are accidentally loaded in the environment.

2. **Service Connectivity:**
   - Pings the PostgreSQL database to verify connection and credentials.
   - Pings the Neo4j database to verify connection and credentials.

3. **Data Integrity (Synthetic Check):**
   - Queries PostgreSQL to ensure the expected synthetic demo case (`CASE-2024-SYN-001`) exists.
   - Queries Neo4j to ensure basic nodes and edges (e.g., "John Doe") are present in the graph.

4. **API Health:**
   - Makes a request to the FastAPI `/health` endpoint to ensure the web server is responsive.

## Usage
Run this script prior to any presentation to prevent live errors:
```bash
python scripts/verify_demo_ready.py
```
If all checks pass, the script outputs a success message indicating the demo environment is healthy and ready.
