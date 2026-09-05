"""Authentication endpoints."""

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps.backend.app.api.deps import get_current_active_user
from apps.backend.app.core.config import settings
from apps.backend.app.core.security import create_access_token, verify_password
from apps.backend.app.db.session import get_db
from apps.backend.app.models.user import User
from apps.backend.app.services.audit import log_action, LOGIN_SUCCEEDED, LOGIN_FAILED

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserProfile


@router.post("/login", response_model=LoginResponse)
def login_access_token(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        if user:
            log_action(
                db=db,
                action=LOGIN_FAILED,
                target_type="USER",
                target_id=user.id,
                user_id=user.id,
                rationale="Invalid credentials"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        log_action(
            db=db,
            action=LOGIN_FAILED,
            target_type="USER",
            target_id=user.id,
            user_id=user.id,
            rationale="Inactive user"
        )
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    log_action(
        db=db,
        action=LOGIN_SUCCEEDED,
        target_type="USER",
        target_id=user.id,
        user_id=user.id,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
    }


@router.get("/me", response_model=UserProfile)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get current user."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
    }
