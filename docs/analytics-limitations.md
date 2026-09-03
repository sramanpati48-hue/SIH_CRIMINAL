# Analytics Limitations and Offline Degradation

SIH 26189 is designed for robust operation in imperfect environments, but it has defined limitations.

## Fallback Mode Limitations
When operating via the Python NetworkX fallback:
1. **Memory Bound:** The `ANALYTICS_MAX_NODES` is strictly capped (e.g., 500) because processing larger graphs entirely in Python memory becomes a bottleneck.
2. **Algorithm Constraints:** We avoid complex community detection (like Louvain) in the Python fallback to maintain fast response times, opting for simpler structural metrics.
3. **No Global Analytics:** The fallback only analyzes the *subgraph for a specific case*. It cannot detect cross-case patterns efficiently across the entire database without Neo4j.

## Offline Degradation
If Neo4j is completely offline:
- **Graph UI:** The `/cases/{caseId}/graph` page will gracefully degrade, informing the user that visualization is offline.
- **Analytics Run:** Clicking "Run Analytics" will return a `GRAPH_UNAVAILABLE` status.
- **Historical Analytics:** Because features and alerts are synchronized back to PostgreSQL upon generation, the **Investigative Leads & Patterns** section remains fully functional. Investigators can still view, review, and act on past alerts.
