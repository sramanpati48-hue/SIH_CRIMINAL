"""Neo4j driver lifecycle management and connection handling."""

import logging
from contextlib import contextmanager
from typing import Generator

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError

from apps.backend.app.core.config import settings

logger = logging.getLogger(__name__)


class Neo4jManager:
    """Manages the Neo4j driver lifecycle."""

    def __init__(self) -> None:
        self._driver: Driver | None = None
        self._is_available: bool = False

    def init_driver(self) -> None:
        """Initialize the driver based on configuration."""
        if not settings.NEO4J_URI:
            logger.warning("NEO4J_URI is not set. Graph features will be offline.")
            return

        try:
            # We delay actual connection check until explicitly requested,
            # but we can create the driver instance.
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info(f"Neo4j driver initialized for URI: {settings.NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {str(e)}")
            self._driver = None

    def close(self) -> None:
        """Close the Neo4j driver."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            self._is_available = False

    def verify_connectivity(self) -> bool:
        """Check if Neo4j is reachable and authentication succeeds."""
        if self._driver is None:
            return False

        try:
            self._driver.verify_connectivity()
            self._is_available = True
            return True
        except (ServiceUnavailable, AuthError) as e:
            logger.warning(f"Neo4j connectivity verification failed: {type(e).__name__}")
            self._is_available = False
            return False
        except Exception as e:
            logger.warning(f"Unexpected error during Neo4j verify_connectivity: {str(e)}")
            self._is_available = False
            return False

    def is_available(self) -> bool:
        """Return True if Neo4j is available."""
        return self._is_available

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a context-managed Neo4j session."""
        if self._driver is None:
            raise RuntimeError("Neo4j driver is not initialized or unavailable.")
        
        session = self._driver.session(database=settings.NEO4J_DATABASE)
        try:
            yield session
        finally:
            session.close()


# Singleton instance
neo4j_manager = Neo4jManager()
