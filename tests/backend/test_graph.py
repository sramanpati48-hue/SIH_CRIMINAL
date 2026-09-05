"""Tests for the Neo4j Graph Integration subsystem."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from apps.backend.app.graph.schema import GraphNode, GraphEdge
from apps.backend.app.graph.service import GraphService, GraphServiceUnavailableError
from apps.backend.app.graph.repository import GraphRepository
from apps.backend.app.graph.driver import neo4j_manager


class TestGraphSchemaValidation:
    """Test Pydantic schema validation for graph models."""

    def test_graph_node_validation(self):
        """Test valid node instantiation."""
        node = GraphNode(
            id="person_123",
            label="Person",
            entity_type="Person",
            properties={"name": "John Doe"},
            case_id="case_1"
        )
        assert node.id == "person_123"
        assert node.label == "Person"

    def test_graph_edge_confidence_bounds(self):
        """Confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            GraphEdge(
                id="edge_1",
                source_id="person_1",
                target_id="person_2",
                relationship_type="CALLED",
                confidence=1.5  # Invalid
            )

        with pytest.raises(ValueError):
            GraphEdge(
                id="edge_1",
                source_id="person_1",
                target_id="person_2",
                relationship_type="CALLED",
                confidence=-0.1  # Invalid
            )


class TestGraphServiceLogic:
    """Test GraphService business logic independently of Neo4j."""

    def test_deterministic_relationship_id(self):
        """Test the generation of deterministic relationship IDs."""
        service = GraphService()
        id1 = service._generate_relationship_id("src1", "tgt1", "CALLED", "doc1", "2026-09-02")
        id2 = service._generate_relationship_id("src1", "tgt1", "CALLED", "doc1", "2026-09-02")
        id3 = service._generate_relationship_id("src2", "tgt1", "CALLED", "doc1", "2026-09-02")

        assert id1 == id2  # Identical inputs produce identical IDs
        assert id1 != id3  # Different inputs produce different IDs

    @patch("apps.backend.app.graph.driver.neo4j_manager.is_available")
    def test_service_unavailable_error(self, mock_is_available):
        """Test service raises GraphServiceUnavailableError when Neo4j is offline."""
        mock_is_available.return_value = False
        service = GraphService()

        with pytest.raises(GraphServiceUnavailableError):
            service.get_case_subgraph("case_1")

        with pytest.raises(GraphServiceUnavailableError):
            service.get_entity_neighbours("Person", "person_1")


class TestGraphRepositoryCypher:
    """Test GraphRepository constructs expected Cypher parameters."""

    def test_create_entity_cypher_parameters(self):
        """Test that repository passes properties as parameters."""
        mock_session = MagicMock()
        mock_session.run.return_value.single.return_value = {"n": {"person_id": "p1", "name": "Test"}}

        repo = GraphRepository(mock_session)
        result = repo.create_or_merge_entity(
            label="Person",
            entity_id="p1",
            properties={"name": "Test"},
            case_id="case1",
            document_ids=["doc1"]
        )

        assert result["person_id"] == "p1"
        mock_session.run.assert_called_once()
        args, kwargs = mock_session.run.call_args
        
        # Ensure parameters are passed correctly
        assert kwargs["entity_id"] == "p1"
        assert kwargs["case_id"] == "case1"
        assert kwargs["properties"] == {"name": "Test"}
        
        # Ensure label was injected into the query safely (allow-listed)
        query = args[0]
        assert "MERGE (n:Person:Entity {person_id: $entity_id})" in query

    def test_invalid_label_rejected(self):
        """Repository must reject non-allow-listed labels to prevent injection."""
        repo = GraphRepository(MagicMock())
        with pytest.raises(ValueError, match="Invalid node label"):
            repo.create_or_merge_entity("HackerLabel", "id", {}, "case", [])

    def test_invalid_relationship_type_rejected(self):
        """Repository must reject non-allow-listed relationship types."""
        repo = GraphRepository(MagicMock())
        with pytest.raises(ValueError, match="Invalid relationship type"):
            repo.create_or_merge_relationship(
                "Person", "p1", "Person", "p2", "DROP_TABLE", "rel1", {}
            )


class TestGraphAPIEndpointsOffline:
    """Test API behavior when Neo4j is offline (mocked)."""

    @patch("apps.backend.app.graph.driver.neo4j_manager.verify_connectivity")
    def test_health_check_offline(self, mock_verify, admin_client):
        """Health check returns 200 OK but indicates offline status."""
        mock_verify.return_value = False
        response = admin_client.get("/api/v1/graph/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"
        assert data["neo4j_available"] is False

    @patch("apps.backend.app.graph.driver.neo4j_manager.is_available")
    def test_get_case_graph_offline(self, mock_is_available, admin_client):
        """Endpoints return 503 when Neo4j is offline."""
        mock_is_available.return_value = False
        response = admin_client.get("/api/v1/cases/case_123/graph")
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()


@pytest.mark.neo4j
class TestGraphIntegration:
    """Integration tests requiring a live Neo4j database."""

    @pytest.fixture(autouse=True)
    def skip_if_no_neo4j(self):
        """Automatically skip these tests if Neo4j is not actually running."""
        neo4j_manager.init_driver()
        if not neo4j_manager.verify_connectivity():
            pytest.skip("Neo4j is not available for integration tests.")
        yield
        neo4j_manager.close()

    def test_neo4j_driver_connection(self):
        """Test the driver can connect and execute a basic query."""
        assert neo4j_manager.is_available()
        with neo4j_manager.get_session() as session:
            result = session.run("RETURN 1 AS n")
            assert result.single()["n"] == 1

    def test_graph_repository_integration(self):
        """Test actual node and relationship creation in Neo4j."""
        with neo4j_manager.get_session() as session:
            repo = GraphRepository(session)
            
            # Clean up before
            repo.clear_demo_graph_by_case_id("test_case_int")
            
            # 1. Initialize constraints (should not fail)
            repo.initialize_constraints()

            # 2. Create entities
            n1 = repo.create_or_merge_entity("Person", "p1", {"name": "Alice"}, "test_case_int", ["doc1"])
            n2 = repo.create_or_merge_entity("Phone", "ph1", {"number": "555-0100"}, "test_case_int", ["doc1"])
            
            assert n1["name"] == "Alice"

            # 3. Create relationship
            service = GraphService()
            rel_id = service._generate_relationship_id("p1", "ph1", "OWNS", "doc1", None)
            
            r = repo.create_or_merge_relationship(
                "Person", "p1", "Phone", "ph1", "OWNS", rel_id, 
                {"confidence": 0.9}
            )
            assert r["confidence"] == 0.9

            # 4. Fetch subgraph
            nodes, edges = repo.get_case_subgraph("test_case_int")
            assert len(nodes) >= 2
            assert len(edges) >= 1

            # Clean up after
            repo.clear_demo_graph_by_case_id("test_case_int")
