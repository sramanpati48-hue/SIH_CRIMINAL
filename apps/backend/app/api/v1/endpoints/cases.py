"""Case API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.backend.app.db.session import get_db
from apps.backend.app.repositories.case_repo import CaseRepository
from apps.backend.app.schemas.case import (
    CaseCreate,
    CaseListResponse,
    CaseResponse,
    CaseStatus,
    CaseUpdate,
)
from apps.backend.app.api.deps import get_current_active_user, require_role, require_case_access
from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
from apps.backend.app.models.case import Case
from apps.backend.app.services.audit import log_action, CASE_CREATED, CASE_UPDATED

router = APIRouter()


def _structured_error(
    status_code: int, code: str, message: str, path: str
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "path": path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new investigation case",
)
def create_case(
    data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.INVESTIGATOR, Role.ADMINISTRATOR])),
) -> CaseResponse:
    """Create a new case. Assign MANAGE access to the creator."""
    repo = CaseRepository(db)
    existing = repo.get_by_case_number(data.case_number)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case with number '{data.case_number}' already exists.",
        )

    try:
        # We inject created_by
        case_data = data.model_dump()
        case = Case(**case_data)
        case.created_by = current_user.id
        db.add(case)
        db.flush()  # to get case.id

        # Grant MANAGE access to the creator automatically if not an administrator
        # (Though we can just grant it to everyone who creates it to be safe)
        access = CaseAccess(
            user_id=current_user.id,
            case_id=case.id,
            access_level=CaseAccessLevel.MANAGE.value,
            assigned_by_user_id=current_user.id,
            is_active=True
        )
        db.add(access)

        log_action(
            db=db,
            action=CASE_CREATED,
            target_type="CASE",
            target_id=case.id,
            user_id=current_user.id,
        )

        db.commit()
        db.refresh(case)
        return CaseResponse.model_validate(case)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case.",
        ) from exc


@router.get(
    "",
    response_model=CaseListResponse,
    summary="List investigation cases",
)
def list_cases(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status_filter: CaseStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CaseListResponse:
    """List cases. Administrators see all, others see assigned."""
    status_value = status_filter.value if status_filter else None

    query = db.query(Case)
    if status_value:
        query = query.filter(Case.status == status_value)

    if current_user.role != Role.ADMINISTRATOR.value:
        query = query.join(CaseAccess).filter(
            CaseAccess.user_id == current_user.id,
            CaseAccess.is_active == True
        )

    total = query.count()
    cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()

    return CaseListResponse(
        total=total,
        cases=[CaseResponse.model_validate(c) for c in cases],
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Get case details",
)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    access: CaseAccess = Depends(require_case_access(CaseAccessLevel.VIEW)),
) -> CaseResponse:
    repo = CaseRepository(db)
    case = repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    return CaseResponse.model_validate(case)


@router.patch(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Update case details",
)
def update_case(
    case_id: str,
    data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    access: CaseAccess = Depends(require_case_access(CaseAccessLevel.MANAGE)),
) -> CaseResponse:
    repo = CaseRepository(db)
    case = repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")
    
    prev_state = {"status": case.status, "priority": case.priority, "title": case.title, "description": case.description}

    try:
        case = repo.update(case_id, data)
        new_state = {"status": case.status, "priority": case.priority, "title": case.title, "description": case.description}
        
        log_action(
            db=db,
            action=CASE_UPDATED,
            target_type="CASE",
            target_id=case.id,
            user_id=current_user.id,
            previous_state=prev_state,
            new_state=new_state
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update case.") from exc

    return CaseResponse.model_validate(case)
