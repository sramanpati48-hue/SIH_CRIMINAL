"""Python (NetworkX) graph feature extraction fallback."""

import datetime
import networkx as nx

from apps.backend.app.graph.schema import GraphResponse
from apps.backend.app.analytics.schemas import EntityGraphFeatures, CaseGraphAnalytics, AnalyticsStatus, AnalyticsEngine
from apps.backend.app.analytics.config import analytics_settings


class NetworkXFeatureExtractor:
    """Calculates graph metrics deterministically using NetworkX."""

    def __init__(self, graph_response: GraphResponse):
        """Initialize and build the NetworkX graph from a bounded GraphResponse."""
        self.graph_response = graph_response
        self.case_id = graph_response.case_id or "UNKNOWN_CASE"
        self.generated_at = graph_response.generated_at
        
        # Build directed graph
        self.G = nx.DiGraph()
        
        for node in graph_response.nodes:
            self.G.add_node(
                node.id, 
                label=node.label,
                entity_type=node.entity_type,
                case_id=node.case_id,
                properties=node.properties
            )
            
        for edge in graph_response.edges:
            # We preserve relationship properties
            self.G.add_edge(
                edge.source_id,
                edge.target_id,
                id=edge.id,
                relationship_type=edge.relationship_type,
                source_document_id=edge.source_document_id,
                event_date=edge.event_date,
                confidence=edge.confidence,
                verified=edge.verified,
                properties=edge.properties
            )
            
        # Build an undirected version for algorithms requiring it (e.g. connected components)
        self.G_undirected = self.G.to_undirected(as_view=True)

    def extract_features(self) -> tuple[dict[str, EntityGraphFeatures], CaseGraphAnalytics]:
        """Extract all graph features deterministically."""
        
        if len(self.G.nodes) == 0:
            # Empty graph
            analytics = CaseGraphAnalytics(
                case_id=self.case_id,
                node_count=0,
                edge_count=0,
                community_count=0,
                density=0.0,
                computed_at=datetime.datetime.now(datetime.timezone.utc),
                algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                analytics_engine=AnalyticsEngine.NETWORKX_FALLBACK,
                status=AnalyticsStatus.NO_GRAPH_DATA,
                warnings=["No graph relationships are available for this case."]
            )
            return {}, analytics

        now = datetime.datetime.now(datetime.timezone.utc)
        warnings = []
        
        if self.graph_response.truncated:
            warnings.append("Graph was truncated. Analytics computed on partial data.")
            
        warnings.append("Neo4j Graph Data Science is unavailable; Python fallback was used.")

        # --- Graph Algorithms ---
        # 1. Pagerank
        try:
            pagerank_scores = nx.pagerank(self.G, alpha=0.85, max_iter=100)
        except nx.PowerIterationFailedConvergence:
            pagerank_scores = {n: 0.0 for n in self.G.nodes}
            
        # 2. Betweenness Centrality
        betweenness_scores = nx.betweenness_centrality(self.G, normalized=True)
        
        # 3. Community Detection (using connected components as a deterministic simple community for small graphs)
        # Using undirected graph to find isolated subgraphs
        communities = list(nx.connected_components(self.G_undirected))
        node_to_community = {}
        community_sizes = {}
        for idx, comm in enumerate(communities):
            cid = f"comm_{idx}"
            size = len(comm)
            community_sizes[cid] = size
            for node in comm:
                node_to_community[node] = cid
                
        # 4. Bridge score (approximate bridge using betweenness and community connectivity)
        # For this MVP, bridge score is just normalized betweenness * community uniqueness, but for simplicity
        # we will just map betweenness directly as it identifies bridge nodes naturally.
        # Alternatively, NetworkX has bridges(), but those are edges.
        # We will use betweenness_centrality as a strong bridge indicator for nodes.

        features_by_id = {}
        
        for node_id, data in self.G.nodes(data=True):
            in_degree = self.G.in_degree(node_id)
            out_degree = self.G.out_degree(node_id)
            degree = in_degree + out_degree
            
            # Sub-features
            unique_neighbors = set(self.G.predecessors(node_id)).union(set(self.G.successors(node_id)))
            
            # specific connectivity counts
            shared_phones = 0
            shared_locations = 0
            shared_vehicles = 0
            transaction_count = 0
            transaction_total = 0.0
            
            for neighbor in unique_neighbors:
                n_data = self.G.nodes[neighbor]
                n_type = n_data.get("entity_type", "")
                if n_type == "PHONE":
                    shared_phones += 1
                elif n_type == "LOCATION":
                    shared_locations += 1
                elif n_type == "VEHICLE":
                    shared_vehicles += 1
                    
            # Transaction specific
            # Look at edges connected to this node
            for u, v, e_data in self.G.edges(node_id, data=True):
                if e_data.get("relationship_type") in ("TRANSFERRED_TO", "PAID"):
                    transaction_count += 1
                    amt = float(e_data.get("properties", {}).get("amount", 0.0))
                    transaction_total += amt
                    
            for u, v, e_data in self.G.in_edges(node_id, data=True):
                if e_data.get("relationship_type") in ("TRANSFERRED_TO", "PAID"):
                    transaction_count += 1
                    amt = float(e_data.get("properties", {}).get("amount", 0.0))
                    transaction_total += amt

            cid = node_to_community.get(node_id)
            csize = community_sizes.get(cid, 0)
            
            feat = EntityGraphFeatures(
                entity_id=node_id,
                case_id=self.case_id,
                entity_type=data.get("entity_type", "UNKNOWN"),
                degree=degree,
                in_degree=in_degree,
                out_degree=out_degree,
                case_count=1, # Single subgraph perspective
                unique_neighbour_count=len(unique_neighbors),
                shared_location_count=shared_locations,
                shared_phone_count=shared_phones,
                shared_vehicle_count=shared_vehicles,
                transaction_count=transaction_count,
                transaction_total=transaction_total,
                transaction_chain_count=0, # Computed higher up if needed
                community_id=cid,
                community_size=csize,
                pagerank_score=pagerank_scores.get(node_id, 0.0),
                betweenness_score=betweenness_scores.get(node_id, 0.0),
                bridge_score=betweenness_scores.get(node_id, 0.0), # Simplified for MVP fallback
                historical_similarity_score=None,
                computed_at=now,
                algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
                analytics_engine=AnalyticsEngine.NETWORKX_FALLBACK,
                warnings=[]
            )
            features_by_id[node_id] = feat
            
        case_analytics = CaseGraphAnalytics(
            case_id=self.case_id,
            node_count=self.G.number_of_nodes(),
            edge_count=self.G.number_of_edges(),
            community_count=len(communities),
            density=nx.density(self.G),
            computed_at=now,
            algorithm_version=analytics_settings.ANALYTICS_ALGORITHM_VERSION,
            analytics_engine=AnalyticsEngine.NETWORKX_FALLBACK,
            status=AnalyticsStatus.COMPLETED_WITH_WARNINGS,
            truncated=self.graph_response.truncated,
            warnings=warnings
        )
        
        return features_by_id, case_analytics
