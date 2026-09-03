"""Graph business logic and mapping layer."""

import hashlib
from datetime import datetime, timezone

from apps.backend.app.graph.driver import neo4j_manager
from apps.backend.app.graph.repository import GraphRepository, STABLE_ID_MAP
from apps.backend.app.graph.schema import (
    GraphEdge,
    GraphNode,
    GraphResponse,
    EntityNeighbourResponse,
    RelationshipEvidenceResponse,
    GraphHealthResponse,
)


class GraphServiceUnavailableError(Exception):
    """Raised when Neo4j is offline or unreachable."""
    pass


class GraphService:
    """Provides high-level graph operations and maps results to Pydantic schemas."""

    def _ensure_available(self) -> None:
        """Check availability before operations to fail fast gracefully."""
        if not neo4j_manager.is_available():
            raise GraphServiceUnavailableError("Graph database is currently unavailable.")

    def _generate_relationship_id(
        self, source_id: str, target_id: str, rel_type: str, doc_id: str | None, event_date: str | None
    ) -> str:
        """Generate a deterministic relationship ID."""
        parts = [source_id, rel_type, target_id, str(doc_id), str(event_date)]
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _map_node(self, raw_node: dict) -> GraphNode:
        """Map raw dictionary to GraphNode schema."""
        # Extract label from dict if available, or determine it from properties
        # Neo4j dict representation of a node usually doesn't have labels easily exposed without the native Node object,
        # but our repository returns `dict(record["n"])` which extracts properties. 
        # We need to deduce label from stable ID presence if possible, or expect it passed.
        # Since we just need the Pydantic schema to be happy for the API:
        
        # Deduce label from properties
        label = "Unknown"
        entity_id = "unknown_id"
        for lbl, prop in STABLE_ID_MAP.items():
            if prop in raw_node:
                label = lbl
                entity_id = raw_node.pop(prop)
                break
        
        # Extract known root fields
        case_id = raw_node.pop("case_id", None)
        # Properties left over
        return GraphNode(
            id=entity_id,
            label=label,
            entity_type=label, # For now, entity type maps to label
            properties=raw_node,
            case_id=case_id,
        )

    def _map_edge(self, raw_edge: dict) -> GraphEdge:
        """Map raw relationship dictionary to GraphEdge schema."""
        rel_id = raw_edge.pop("relationship_id", "unknown")
        doc_id = raw_edge.pop("source_document_id", None)
        src_type = raw_edge.pop("source_type", None)
        event_date_str = raw_edge.pop("event_date", None)
        confidence = raw_edge.pop("confidence", None)
        verified = raw_edge.pop("verified", False)
        
        event_date = None
        if event_date_str:
            try:
                event_date = datetime.fromisoformat(event_date_str)
            except ValueError:
                pass
                
        # We might not have source/target IDs in the raw edge properties natively if they are just the relationship's properties.
        # This requires the repo to return them or we extract them. The simplest MVP approach sets them to "unknown"
        # unless explicitly saved as properties on the edge during creation. We save them as properties for simplicity.
        src_id = raw_edge.pop("source_id", "unknown")
        tgt_id = raw_edge.pop("target_id", "unknown")
        rel_type = raw_edge.pop("relationship_type", "UNKNOWN")

        return GraphEdge(
            id=rel_id,
            source_id=src_id,
            target_id=tgt_id,
            relationship_type=rel_type,
            properties=raw_edge,
            source_document_id=doc_id,
            source_type=src_type,
            event_date=event_date,
            confidence=confidence,
            verified=verified,
        )

    def health_check(self) -> GraphHealthResponse:
        """Return the health status of the graph database."""
        is_available = neo4j_manager.verify_connectivity()
        status = "healthy" if is_available else "unavailable"
        
        return GraphHealthResponse(
            status=status,
            neo4j_available=is_available,
            database="neo4j", # Generic placeholder
            checked_at=datetime.now(timezone.utc),
            message="Neo4j is online." if is_available else "Neo4j is offline or unreachable."
        )

    def get_case_subgraph(self, case_id: str, limit: int = 500) -> GraphResponse:
        """Retrieve the graph for a specific case."""
        self._ensure_available()
        
        with neo4j_manager.get_session() as session:
            repo = GraphRepository(session)
            raw_nodes, raw_edges = repo.get_case_subgraph(case_id, limit=limit)
            
            return GraphResponse(
                case_id=case_id,
                nodes=[self._map_node(n) for n in raw_nodes],
                edges=[self._map_edge(e) for e in raw_edges],
                generated_at=datetime.now(timezone.utc),
                truncated=len(raw_nodes) >= limit or len(raw_edges) >= limit
            )

    def get_entity_neighbours(self, label: str, entity_id: str, limit: int = 100) -> EntityNeighbourResponse | None:
        """Retrieve an entity and its immediate neighbours."""
        self._ensure_available()
        
        with neo4j_manager.get_session() as session:
            repo = GraphRepository(session)
            entity_raw, neighbours_raw, edges_raw = repo.get_entity_neighbours(label, entity_id, limit=limit)
            
            if not entity_raw:
                return None
                
            return EntityNeighbourResponse(
                entity=self._map_node(entity_raw),
                neighbours=[self._map_node(n) for n in neighbours_raw],
                relationships=[self._map_edge(e) for e in edges_raw]
            )

    def get_relationship_evidence(self, relationship_id: str) -> RelationshipEvidenceResponse | None:
        """Retrieve evidence details for a specific relationship."""
        self._ensure_available()
        
        with neo4j_manager.get_session() as session:
            repo = GraphRepository(session)
            edge_raw = repo.get_relationship_evidence(relationship_id)
            
            if not edge_raw:
                return None
                
            edge = self._map_edge(edge_raw)
            return RelationshipEvidenceResponse(
                relationship_id=edge.id,
                relationship_type=edge.relationship_type,
                source_id=edge.source_id,
                target_id=edge.target_id,
                source_document_id=edge.source_document_id,
                source_type=edge.source_type,
                event_date=edge.event_date,
                confidence=edge.confidence,
                verified=edge.verified,
                evidence_text=edge.properties.get("evidence_text")
            )
