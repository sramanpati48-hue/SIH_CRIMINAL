"""Document repository — database access for Document operations."""

import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from apps.backend.app.models.document import Document
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.schemas.document import DocumentCreate


class DocumentRepository:
    """Encapsulates all Document database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self, case_id: str, data: DocumentCreate, uploaded_by: str | None = None
    ) -> Document:
        """Create a document record linked to a case and log the action."""
        file_hash: str | None = None
        if data.raw_content:
            file_hash = hashlib.sha256(data.raw_content.encode("utf-8")).hexdigest()

        doc = Document(
            case_id=case_id,
            file_name=data.file_name,
            file_type=data.file_type.value,
            raw_content=data.raw_content,
            file_hash=file_hash,
            status="UPLOADED",
            uploaded_by=uploaded_by,
        )
        self.db.add(doc)
        self.db.flush()

        audit = AuditLog(
            action="UPLOAD_DOCUMENT",
            target_type="DOCUMENT",
            target_id=doc.id,
            new_state=f'{{"file_name": "{doc.file_name}", "case_id": "{case_id}"}}',
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, document_id: str) -> Document | None:
        """Retrieve a single document by its UUID."""
        return (
            self.db.query(Document).filter(Document.id == document_id).first()
        )

    def list_by_case(
        self, case_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[Document], int]:
        """List documents belonging to a case with pagination."""
        query = self.db.query(Document).filter(Document.case_id == case_id)
        total = query.count()
        docs = (
            query.order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return docs, total
