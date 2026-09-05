"""API dependencies."""

from typing import Callable, Any, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from apps.backend.app.core.config import settings
from apps.backend.app.core.security import ALGORITHM
from apps.backend.app.db.session import get_db
from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
from apps.backend.app.models.case import Case
from apps.backend.app.services.audit import log_action

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Validate JWT and fetch user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Strict algorithm validation
        unverified_headers = jwt.get_unverified_headers(token)
        if unverified_headers.get("alg") != ALGORITHM:
            raise credentials_exception

        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_sub": True,
                "require_exp": True,
                "require_sub": True
            }
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
            
        jti: str = payload.get("jti")
        if not jti:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return current_user


def require_role(allowed_roles: list[Role]) -> Callable[[User], User]:
    """Dependency to check if the user has one of the allowed roles."""
    def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[Session, Depends(get_db)]
    ) -> User:
        if current_user.role not in [role.value for role in allowed_roles]:
            log_action(
                db=db,
                action="AUTHORIZATION_DENIED",
                user_id=current_user.id,
                target_type="ROLE",
                target_id=current_user.role,
                new_state={"reason": f"Required one of {[r.value for r in allowed_roles]}, had {current_user.role}"}
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
    return role_checker


def require_administrator(
    current_user: Annotated[User, Depends(require_role([Role.ADMINISTRATOR]))],
) -> User:
    """Dependency for requiring administrator privileges."""
    return current_user


def require_case_access(required_level: CaseAccessLevel) -> Callable[[str, User, Session], CaseAccess]:
    """Dependency to check if the user has sufficient access level for a case."""
    def access_checker(
        case_id: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> CaseAccess:
        # Administrator has implicit MANAGE access to all cases
        if current_user.role == Role.ADMINISTRATOR.value:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                raise HTTPException(status_code=404, detail="Case not found")
            return CaseAccess(
                user_id=current_user.id,
                case_id=case_id,
                access_level=CaseAccessLevel.MANAGE.value,
                is_active=True
            )

        # For normal users, check case_access assignment
        assignment = db.query(CaseAccess).filter(
            CaseAccess.case_id == case_id,
            CaseAccess.user_id == current_user.id,
            CaseAccess.is_active == True
        ).first()

        if not assignment:
            log_action(
                db=db,
                action="AUTHORIZATION_DENIED",
                user_id=current_user.id,
                target_type="CASE",
                target_id=case_id,
                new_state={"reason": "User is not assigned to this case"}
            )
            db.commit()
            raise HTTPException(status_code=403, detail="Not assigned to this case")

        assigned_level = CaseAccessLevel(assignment.access_level)
        if not assigned_level.includes(required_level):
            log_action(
                db=db,
                action="AUTHORIZATION_DENIED",
                user_id=current_user.id,
                target_type="CASE",
                target_id=case_id,
                new_state={"reason": f"Requires {required_level.value} access, had {assigned_level.value}"}
            )
            db.commit()
            raise HTTPException(status_code=403, detail=f"Requires {required_level.value} access to this case")

        return assignment
    return access_checker
