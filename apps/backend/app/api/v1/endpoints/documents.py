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
) -> DocumentResponse:
    """Create a new document record for a case."""
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )

    doc_repo = DocumentRepository(db)
    try:
        doc = doc_repo.create(case_id=case_id, data=data)
        return DocumentResponse.model_validate(doc)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document.",
        ) from exc


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
) -> DocumentListResponse:
    """List all documents belonging to a specific case."""
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_id}' not found.",
        )

    doc_repo = DocumentRepository(db)
    docs, total = doc_repo.list_by_case(case_id=case_id, skip=skip, limit=limit)
    return DocumentListResponse(
        total=total,
        documents=[DocumentResponse.model_validate(d) for d in docs],
    )
