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

router = APIRouter()


def _structured_error(
    status_code: int, code: str, message: str, path: str
) -> JSONResponse:
    """Return a structured error response."""
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
) -> CaseResponse:
    """Create a new case. Case numbers must be unique."""
    repo = CaseRepository(db)

    # Check for duplicate case number
    existing = repo.get_by_case_number(data.case_number)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case with number '{data.case_number}' already exists.",
        )

    try:
        case = repo.create(data)
        return CaseResponse.model_validate(case)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case. Please check input and retry.",
        ) from exc


@router.get(
    "",
    response_model=CaseListResponse,
    summary="List investigation cases",
)
def list_cases(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum records to return"),
    status_filter: CaseStatus | None = Query(
        default=None, alias="status", description="Filter by case status"
    ),
    db: Session = Depends(get_db),
) -> CaseListResponse:
    """List all cases with optional status filter and pagination."""
    repo = CaseRepository(db)
    status_value = status_filter.value if status_filter else None
    cases, total = repo.list_all(skip=skip, limit=limit, status=status_value)
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
) -> CaseResponse:
    """Retrieve a specific case by ID."""
    repo = CaseRepository(db)
    case = repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )
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
) -> CaseResponse:
    """Partially update a case. Only provided fields are changed."""
    repo = CaseRepository(db)

    try:
        case = repo.update(case_id, data)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update case.",
        ) from exc

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )
    return CaseResponse.model_validate(case)
