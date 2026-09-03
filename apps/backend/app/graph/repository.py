"""Graph database repository for executing Cypher queries safely."""

import logging
from typing import Any

from neo4j import Session

logger = logging.getLogger(__name__)

# Allow-lists to prevent Cypher injection via dynamic labels/types
VALID_NODE_LABELS = {
    "Person", "Phone", "Vehicle", "Location", "Organization", "BankAccount", 
    "Case", "Document", "Event", "Entity"
}

VALID_RELATIONSHIP_TYPES = {
    "CALLED", "USED", "OWNS", "VISITED", "TRANSFERRED_TO", "INVOLVED_IN", 
    "MENTIONED_IN", "CONNECTED_TO", "OCCURRED_AT"
}

# Mapping of specific labels to their stable ID property names
STABLE_ID_MAP = {
    "Person": "person_id",
    "Phone": "phone_id",
    "Vehicle": "vehicle_id",
    "Location": "location_id",
    "Organization": "organization_id",
    "BankAccount": "account_id",
    "Case": "case_id",
    "Document": "document_id",
    "Event": "event_id",
}


class GraphRepository:
    """Encapsulates Neo4j Cypher operations with safe parameterization."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def initialize_constraints(self) -> None:
        """Create uniqueness constraints for stable IDs."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Phone) REQUIRE p.phone_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.vehicle_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (o:Organization) REQUIRE o.organization_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (b:BankAccount) REQUIRE b.account_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.document_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:CALLED]-() REQUIRE r.relationship_id IS UNIQUE", # Relationship constraints require Neo4j Enterprise (version 5.7+), but we will attempt or gracefully handle.
        ]
        
        # We will attempt to run node constraints. If Neo4j version doesn't support IF NOT EXISTS for some reason, we catch it.
        for query in constraints[:9]: # only node constraints which are widely supported in Community Edition
            try:
                self.session.run(query)
            except Exception as e:
                logger.warning(f"Failed to create constraint ({query}): {str(e)}")

    def _validate_label(self, label: str) -> None:
        if label not in VALID_NODE_LABELS:
            raise ValueError(f"Invalid node label: {label}")

    def _validate_rel_type(self, rel_type: str) -> None:
        if rel_type not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(f"Invalid relationship type: {rel_type}")

    def create_or_merge_case(self, case_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        """Merge a Case node."""
        query = """
        MERGE (c:Case {case_id: $case_id})
        SET c += $properties
        RETURN c
        """
        result = self.session.run(query, case_id=case_id, properties=properties)
        record = result.single()
        return dict(record["c"]) if record else {}

    def create_or_merge_document(self, document_id: str, case_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        """Merge a Document node and link it to its Case."""
        query = """
        MERGE (d:Document {document_id: $document_id})
        SET d += $properties
        MERGE (c:Case {case_id: $case_id})
        MERGE (d)-[:BELONGS_TO]->(c)
        RETURN d
        """
        result = self.session.run(query, document_id=document_id, case_id=case_id, properties=properties)
        record = result.single()
        return dict(record["d"]) if record else {}

    def create_or_merge_entity(self, label: str, entity_id: str, properties: dict[str, Any], case_id: str, document_ids: list[str]) -> dict[str, Any]:
        """Merge an Entity node with a specific label, the Entity label, and link to docs/case."""
        self._validate_label(label)
        id_property = STABLE_ID_MAP.get(label)
        if not id_property:
            raise ValueError(f"No stable ID property mapping for label {label}")

        # Construct safe cypher with allow-listed label
        query = f"""
        MERGE (n:{label}:Entity {{{id_property}: $entity_id}})
        SET n += $properties, n.case_id = $case_id
        WITH n
        UNWIND $document_ids AS doc_id
        MERGE (d:Document {{document_id: doc_id}})
        MERGE (n)-[:MENTIONED_IN]->(d)
        RETURN n
        """
        result = self.session.run(query, entity_id=entity_id, properties=properties, case_id=case_id, document_ids=document_ids)
        record = result.single()
        return dict(record["n"]) if record else {}

    def create_or_merge_event(self, event_id: str, properties: dict[str, Any], case_id: str) -> dict[str, Any]:
        """Merge an Event node."""
        query = """
        MERGE (e:Event:Entity {event_id: $event_id})
        SET e += $properties, e.case_id = $case_id
        RETURN e
        """
        result = self.session.run(query, event_id=event_id, properties=properties, case_id=case_id)
        record = result.single()
        return dict(record["e"]) if record else {}

    def create_or_merge_relationship(
        self,
        source_label: str,
        source_id: str,
        target_label: str,
        target_id: str,
        rel_type: str,
        relationship_id: str,
        properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge a relationship between two nodes."""
        self._validate_label(source_label)
        self._validate_label(target_label)
        self._validate_rel_type(rel_type)

        source_id_prop = STABLE_ID_MAP[source_label]
        target_id_prop = STABLE_ID_MAP[target_label]

        # Use allow-listed labels and types directly in query string
        query = f"""
        MATCH (src:{source_label} {{{source_id_prop}: $source_id}})
        MATCH (tgt:{target_label} {{{target_id_prop}: $target_id}})
        MERGE (src)-[r:{rel_type} {{relationship_id: $relationship_id}}]->(tgt)
        SET r += $properties
        RETURN r
        """
        result = self.session.run(query, source_id=source_id, target_id=target_id, relationship_id=relationship_id, properties=properties)
        record = result.single()
        return dict(record["r"]) if record else {}

    def get_case_subgraph(self, case_id: str, limit: int = 500) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Retrieve all nodes and intra-case relationships for a given case."""
        query = """
        MATCH (n {case_id: $case_id})
        OPTIONAL MATCH (n)-[r]->(m {case_id: $case_id})
        RETURN collect(DISTINCT n) AS nodes, collect(DISTINCT r) AS edges
        """
        result = self.session.run(query, case_id=case_id)
        record = result.single()
        
        nodes = []
        edges = []
        if record:
            nodes = [dict(n) for n in record["nodes"]]
            edges = [dict(r) for r in record["edges"] if r is not None]
        
        # Apply truncation if needed based on limit in service layer, 
        # but returning raw list here.
        return nodes[:limit], edges[:limit]

    def get_entity_neighbours(self, label: str, entity_id: str, limit: int = 100) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        """Retrieve an entity and its immediate 1-hop neighbours."""
        self._validate_label(label)
        id_prop = STABLE_ID_MAP[label]
        
        query = f"""
        MATCH (n:{label} {{{id_prop}: $entity_id}})
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n AS entity, collect(DISTINCT m)[0..$limit] AS neighbours, collect(DISTINCT r)[0..$limit] AS edges
        """
        result = self.session.run(query, entity_id=entity_id, limit=limit)
        record = result.single()
        
        if not record or not record["entity"]:
            return {}, [], []
            
        entity = dict(record["entity"])
        neighbours = [dict(n) for n in record["neighbours"] if n is not None]
        edges = [dict(r) for r in record["edges"] if r is not None]
        
        return entity, neighbours, edges

    def get_relationship_evidence(self, relationship_id: str) -> dict[str, Any] | None:
        """Retrieve a specific relationship's metadata by its ID."""
        query = """
        MATCH ()-[r {relationship_id: $relationship_id}]->()
        RETURN r
        """
        result = self.session.run(query, relationship_id=relationship_id)
        record = result.single()
        return dict(record["r"]) if record else None

    def clear_demo_graph_by_case_id(self, case_id: str) -> int:
        """Delete all nodes and relationships associated with a case ID."""
        query = """
        MATCH (n {case_id: $case_id})
        DETACH DELETE n
        RETURN count(n) AS deleted_count
        """
        result = self.session.run(query, case_id=case_id)
        record = result.single()
        return record["deleted_count"] if record else 0
