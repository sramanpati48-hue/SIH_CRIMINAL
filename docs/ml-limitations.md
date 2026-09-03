# ML Limitations & Security Policy

## Baseline Model Boundaries
1. **No Production GNN:** We do not employ Graph Neural Networks (GNNs) like GraphSAGE or GCN in this milestone. Embeddings are simulated/unavailable and default to engineered `feature_vector`s.
2. **Small Dataset Safe-Guards:** The Random Forest baseline will stubbornly refuse to train if it has fewer than `MIN_SUPERVISED_CASES` (20) to prevent hallucinated confidence scores.
3. **Synthetic Constraints:** The Isolation Forest only knows "anomaly" relative to the synthetic baseline. Legitimate high-connectivity entities (like a real estate agent) may be flagged if the synthetic generator didn't include enough normal highly-connected nodes.

## Artifact Security Policy
- **Trusted Origins:** The application only loads artifacts (models/scalers) it generated itself. 
- **Checksum Verification:** Every artifact produces an SHA-256 checksum during training, which is recorded in the PostgreSQL database.
- **No Untrusted Pickles:** Before loading a model via `joblib` or `pickle`, the artifact's hash is compared against the database. If verification fails, the artifact is rejected, and a safe error is returned.
- **Filesystem Isolation:** Model paths are never exposed via the API.
