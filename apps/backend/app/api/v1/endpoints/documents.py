"""Document API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.backend.app.db.session import get_db
from apps.backend.app.repositories.case_repo import CaseRepository
from apps.backend.app.repositories.document_repo import DocumentRepository
from apps.backend.app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
)
from apps.backend.app.api.deps import get_current_active_user, require_role, require_case_access
from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
from apps.backend.app.services.audit import log_action, DOCUMENT_UPLOADED

router = APIRouter()


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to a case",
)
def create_document(
    case_id: str,
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.INVESTIGATOR, Role.ADMINISTRATOR])),
    access: CaseAccess = Depends(require_case_access(CaseAccessLevel.MANAGE)),
) -> DocumentResponse:
    """Create a new document record for a case."""
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    doc_repo = DocumentRepository(db)
    try:
        doc = doc_repo.create(case_id=case_id, data=data)
        log_action(
            db=db,
            action=DOCUMENT_UPLOADED,
            target_type="DOCUMENT",
            target_id=doc.id,
            user_id=current_user.id,
        )
        db.commit()
        return DocumentResponse.model_validate(doc)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload document.") from exc


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List documents for a case",
)
def list_documents(
    case_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    access: CaseAccess = Depends(require_case_access(CaseAccessLevel.VIEW)),
) -> DocumentListResponse:
    """List all documents belonging to a specific case."""
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found.")

    doc_repo = DocumentRepository(db)
    docs, total = doc_repo.list_by_case(case_id=case_id, skip=skip, limit=limit)
    return DocumentListResponse(
        total=total,
        documents=[DocumentResponse.model_validate(d) for d in docs],
    )
