"""Security utilities and hashing."""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt

from apps.backend.app.core.config import settings

ALGORITHM = "HS256"


def validate_password_policy(password: str) -> None:
    """Validate password against security policy before hashing."""
    if not password:
        raise ValueError("Password cannot be empty.")
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long.")
    
    # Check max length in UTF-8 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > settings.MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError(f"Password exceeds maximum allowed length of {settings.MAX_BCRYPT_PASSWORD_BYTES} bytes.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed one in constant time."""
    try:
        # Avoid crashing if someone passes a >72 byte password to verify
        validate_password_policy(plain_password)
    except ValueError:
        return False
        
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """Generate a bcrypt password hash."""
    validate_password_policy(password)
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(
    subject: str | Any, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a new JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    import uuid
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
