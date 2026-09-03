"""Graph API endpoints for retrieving network data and health."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from apps.backend.app.graph.service import GraphService, GraphServiceUnavailableError
from apps.backend.app.graph.schema import (
    GraphResponse,
    EntityNeighbourResponse,
    RelationshipEvidenceResponse,
    GraphHealthResponse,
)

router = APIRouter()


def get_graph_service() -> GraphService:
    """Dependency provider for GraphService."""
    return GraphService()


@router.get(
    "/graph/health",
    response_model=GraphHealthResponse,
    summary="Check Neo4j graph database health",
)
def check_graph_health(service: GraphService = Depends(get_graph_service)) -> GraphHealthResponse:
    """Returns the availability and status of the Neo4j graph database."""
    # This must work even if offline
    return service.health_check()


@router.get(
    "/cases/{case_id}/graph",
    response_model=GraphResponse,
    summary="Retrieve the graph for a case",
)
def get_case_graph(
    case_id: str,
    limit: int = Query(default=500, ge=1, le=2000, description="Max nodes/edges to retrieve"),
    service: GraphService = Depends(get_graph_service),
) -> GraphResponse:
    """Retrieve the full graph (nodes and relationships) associated with a case. Development only."""
    try:
        return service.get_case_subgraph(case_id, limit=limit)
    except GraphServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the graph."
        )


@router.get(
    "/entities/{entity_id}/neighbours",
    response_model=EntityNeighbourResponse,
    summary="Retrieve an entity and its neighbours",
)
def get_entity_neighbours(
    entity_id: str,
    label: str = Query(..., description="The label of the entity (e.g., Person, Phone)"),
    limit: int = Query(default=100, ge=1, le=500),
    service: GraphService = Depends(get_graph_service),
) -> EntityNeighbourResponse:
    """Retrieve an entity and its immediate (1-hop) neighbours. Development only."""
    try:
        response = service.get_entity_neighbours(label, entity_id, limit=limit)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity {entity_id} with label {label} not found."
            )
        return response
    except GraphServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc)
        )
    except ValueError as exc:
        # e.g., Invalid label
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving entity neighbours."
        )


@router.get(
    "/relationships/{relationship_id}/evidence",
    response_model=RelationshipEvidenceResponse,
    summary="Retrieve relationship evidence details",
)
def get_relationship_evidence(
    relationship_id: str,
    service: GraphService = Depends(get_graph_service),
) -> RelationshipEvidenceResponse:
    """Retrieve evidence text and metadata for a specific relationship. Development only."""
    try:
        response = service.get_relationship_evidence(relationship_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Relationship {relationship_id} not found."
            )
        return response
    except GraphServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving relationship evidence."
        )
