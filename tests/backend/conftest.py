"""Test configuration — provides an isolated in-memory SQLite database for each test session."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from apps.backend.app.db.base import Base
from apps.backend.app.db.session import get_db
from apps.backend.app.main import app

# Import all models so Base.metadata.create_all picks them up
from apps.backend.app.models.user import User  # noqa: F401
from apps.backend.app.models.case import Case  # noqa: F401
from apps.backend.app.models.document import Document  # noqa: F401
from apps.backend.app.models.entity import ExtractedEntity  # noqa: F401
from apps.backend.app.models.relationship import ExtractedRelationship  # noqa: F401
from apps.backend.app.models.processing_job import ProcessingJob  # noqa: F401
from apps.backend.app.models.alert import Alert  # noqa: F401
from apps.backend.app.models.feedback import InvestigatorFeedback  # noqa: F401
from apps.backend.app.models.audit_log import AuditLog  # noqa: F401
from apps.backend.app.models.case_access import CaseAccess  # noqa: F401


TEST_DATABASE_URL = "sqlite:///./test_sih.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override the get_db dependency to use the test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before the test session and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Truncate all tables between individual tests for isolation."""
    yield
    db = TestSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


from apps.backend.app.core.security import get_password_hash, create_access_token
from apps.backend.app.models.user import Role


@pytest.fixture
def unauthenticated_client() -> TestClient:
    """Provide an unauthenticated TestClient."""
    return TestClient(app)


@pytest.fixture
def test_users(db_session: Session) -> dict[str, User]:
    """Create a set of standard test users with different roles."""
    users = {}
    for role in [Role.ADMINISTRATOR, Role.INVESTIGATOR, Role.ANALYST, Role.REVIEWER]:
        username = f"test_{role.value.lower()}"
        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=get_password_hash("testpassword"),
            role=role.value,
            is_active=True
        )
        db_session.add(user)
        users[role.value] = user
    db_session.commit()
    for user in users.values():
        db_session.refresh(user)
    return users


def _get_auth_client(role: Role, test_users: dict[str, User]) -> TestClient:
    """Helper to create an authenticated client."""
    user = test_users[role.value]
    token = create_access_token(subject=user.id)
    c = TestClient(app)
    c.headers.update({"Authorization": f"Bearer {token}"})
    return c


@pytest.fixture
def admin_client(test_users: dict[str, User]) -> TestClient:
    return _get_auth_client(Role.ADMINISTRATOR, test_users)


@pytest.fixture
def investigator_client(test_users: dict[str, User]) -> TestClient:
    return _get_auth_client(Role.INVESTIGATOR, test_users)


@pytest.fixture
def analyst_client(test_users: dict[str, User]) -> TestClient:
    return _get_auth_client(Role.ANALYST, test_users)


@pytest.fixture
def reviewer_client(test_users: dict[str, User]) -> TestClient:
    return _get_auth_client(Role.REVIEWER, test_users)


@pytest.fixture
def db_session() -> Session:
    """Provide a raw SQLAlchemy session for direct DB assertions."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
