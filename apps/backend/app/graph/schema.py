"""Graph Pydantic schemas for the Neo4j subsystem."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Represents a node in the Neo4j graph."""

    id: str = Field(..., description="Stable node identifier (e.g., person_id, case_id)")
    label: str = Field(..., description="Primary node label (e.g., Person, Case)")
    entity_type: str = Field(..., description="Entity type classification")
    properties: dict[str, Any] = Field(default_factory=dict, description="Node properties")
    case_id: str | None = Field(default=None, description="Originating case ID, if applicable")
    source_document_ids: list[str] = Field(default_factory=list, description="IDs of documents supporting this node")


class GraphEdge(BaseModel):
    """Represents a relationship (edge) in the Neo4j graph."""

    id: str = Field(..., description="Deterministic relationship identifier")
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Relationship type (e.g., CALLED, TRANSFERRED_TO)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Relationship properties")
    source_document_id: str | None = Field(default=None, description="Supporting document ID")
    source_type: str | None = Field(default=None, description="Type of the source document/evidence")
    event_date: datetime | None = Field(default=None, description="Date the event occurred")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="Confidence score")
    verified: bool = Field(default=False, description="Whether human-verified")


class GraphResponse(BaseModel):
    """Response containing a subgraph."""

    case_id: str | None = Field(default=None)
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    generated_at: datetime
    truncated: bool = Field(default=False, description="Whether graph exceeds bounds")


class EntityNeighbourResponse(BaseModel):
    """Response containing an entity and its immediate neighbors."""

    entity: GraphNode
    neighbours: list[GraphNode]
    relationships: list[GraphEdge]


class RelationshipEvidenceResponse(BaseModel):
    """Response for relationship evidence."""

    relationship_id: str
    relationship_type: str
    source_id: str
    target_id: str
    source_document_id: str | None = None
    source_type: str | None = None
    event_date: datetime | None = None
    confidence: float | None = None
    verified: bool
    evidence_text: str | None = None


class GraphHealthResponse(BaseModel):
    """Response for graph health check."""

    status: str = Field(..., description="Overall health status ('healthy' or 'unavailable')")
    neo4j_available: bool = Field(..., description="True if Neo4j is reachable")
    database: str = Field(..., description="Target database name")
    checked_at: datetime
    message: str | None = None
