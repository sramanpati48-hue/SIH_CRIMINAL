"""Tests for security and password hardening."""

import pytest
from datetime import timedelta
from jose import jwt
from fastapi.testclient import TestClient

from apps.backend.app.core.config import settings
from apps.backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ALGORITHM
)

def test_password_policy_empty():
    """Empty password should be rejected."""
    with pytest.raises(ValueError, match="cannot be empty"):
        get_password_hash("")

def test_password_policy_short():
    """Short passwords should be rejected."""
    with pytest.raises(ValueError, match="must be at least"):
        get_password_hash("short")

def test_password_policy_valid():
    """Valid password should be hashed."""
    hashed = get_password_hash("ValidPassword123!")
    assert hashed != "ValidPassword123!"
    assert verify_password("ValidPassword123!", hashed) is True

def test_password_policy_exact_max_bytes():
    """Password of exactly 72 UTF-8 bytes is allowed."""
    pwd = "a" * 72
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True

def test_password_policy_exceeds_max_bytes():
    """Password exceeding 72 UTF-8 bytes is rejected."""
    pwd = "a" * 73
    with pytest.raises(ValueError, match="exceeds maximum allowed length"):
        get_password_hash(pwd)

def test_password_policy_unicode_exceeds_max_bytes():
    """Unicode password exceeding 72 bytes is rejected."""
    # A single emoji can be 4 bytes
    pwd = "😀" * 19 # 19 * 4 = 76 bytes
    with pytest.raises(ValueError, match="exceeds maximum allowed length"):
        get_password_hash(pwd)

def test_verify_password_invalid_hash():
    """Invalid hash format returns False, not crash."""
    assert verify_password("ValidPassword123!", "invalidhash") is False

def test_verify_password_long_input():
    """Verifying with a too-long password should not crash, just return False."""
    hashed = get_password_hash("ValidPassword123!")
    long_pwd = "a" * 73
    assert verify_password(long_pwd, hashed) is False

def test_jwt_creation_and_validation():
    """JWT should contain correct algorithm and claims."""
    token = create_access_token(subject="user123")
    unverified_headers = jwt.get_unverified_headers(token)
    assert unverified_headers["alg"] == ALGORITHM
    
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[ALGORITHM],
        options={"verify_exp": True, "verify_sub": True}
    )
    assert payload["sub"] == "user123"
    assert "exp" in payload
    assert "jti" in payload

def test_expired_token(unauthenticated_client: TestClient, test_users):
    """Test that expired token returns 401."""
    # Create an expired token manually
    token = create_access_token(subject="user123", expires_delta=timedelta(minutes=-10))
    response = unauthenticated_client.get(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_invalid_algorithm_token(unauthenticated_client: TestClient, test_users):
    """Test that a token signed with another algorithm is rejected."""
    # Create token with "none" or different algorithm
    to_encode = {"sub": "test_investigator"}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS512")
    response = unauthenticated_client.get(
        "/api/v1/cases",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
