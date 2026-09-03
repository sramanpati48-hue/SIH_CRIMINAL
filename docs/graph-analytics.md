# Graph Analytics Engine

The Analytics Engine in SIH 26189 calculates core structural features for entities within a case network.

## Architecture

The system uses a coordinator pattern `GraphAnalyticsEngine` that dynamically selects the backend:
1. **Neo4j Graph Data Science (GDS):** (Planned) For enterprise deployments.
2. **Python NetworkX Fallback:** (Current Default) For offline, container-less, or GDS-lacking environments. Extracts the subgraph to memory and calculates deterministic metrics using `networkx`.

## Metrics Computed

- **Degree (Total, In, Out):** Identifies highly active entities.
- **PageRank:** Identifies the most influential entities within the subgraph.
- **Betweenness Centrality:** Identifies "brokers" or "bridges" that connect otherwise disparate clusters.
- **Bridge Score:** A normalized metric indicating a node's capacity to facilitate covert communication across groups.
- **Shared Resource Counts:** Pre-calculates `shared_phone_count`, `shared_location_count`, `shared_vehicle_count` for rapid anomaly detection.

## Idempotency

Analytics results are versioned using an `analysis_run_id` based on:
- Case ID
- Graph timestamp (state of the network)
- Algorithm version

If you request analytics on an unchanged graph, it will re-return the existing results, preventing duplicate alerts and saving compute resources. Results are saved in PostgreSQL to ensure the frontend can display analytics even when the graph database is offline.
