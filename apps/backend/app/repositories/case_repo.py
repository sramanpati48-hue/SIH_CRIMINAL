"""Case repository — database access for Case operations."""

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.backend.app.models.case import Case
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.schemas.case import CaseCreate, CaseUpdate


class CaseRepository:
    """Encapsulates all Case database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: CaseCreate, created_by: str | None = None) -> Case:
        """Create a new case and log the action."""
        case = Case(
            case_number=data.case_number,
            title=data.title,
            description=data.description,
            priority=data.priority.value,
            status="ACTIVE",
            created_by=created_by,
        )
        self.db.add(case)
        self.db.flush()  # Populate case.id before audit log

        audit = AuditLog(
            action="CREATE_CASE",
            target_type="CASE",
            target_id=case.id,
            new_state=f'{{"case_number": "{case.case_number}", "title": "{case.title}"}}',
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get_by_id(self, case_id: str) -> Case | None:
        """Retrieve a single case by its UUID."""
        return self.db.query(Case).filter(Case.id == case_id).first()

    def get_by_case_number(self, case_number: str) -> Case | None:
        """Retrieve a single case by its unique case number."""
        return (
            self.db.query(Case).filter(Case.case_number == case_number).first()
        )

    def list_all(
        self, skip: int = 0, limit: int = 50, status: str | None = None
    ) -> tuple[list[Case], int]:
        """List cases with optional status filter and pagination."""
        query = self.db.query(Case)
        if status:
            query = query.filter(Case.status == status)
        total = query.count()
        cases = (
            query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
        )
        return cases, total

    def update(self, case_id: str, data: CaseUpdate) -> Case | None:
        """Partially update a case and log the change."""
        case = self.get_by_id(case_id)
        if case is None:
            return None

        previous_state_parts: list[str] = []
        new_state_parts: list[str] = []
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            old_val = getattr(case, field)
            new_val = value.value if hasattr(value, "value") else value
            previous_state_parts.append(f'"{field}": "{old_val}"')
            new_state_parts.append(f'"{field}": "{new_val}"')
            setattr(case, field, new_val)

        case.updated_at = datetime.now(timezone.utc)
        self.db.flush()

        if previous_state_parts:
            audit = AuditLog(
                action="UPDATE_CASE",
                target_type="CASE",
                target_id=case.id,
                previous_state="{" + ", ".join(previous_state_parts) + "}",
                new_state="{" + ", ".join(new_state_parts) + "}",
            )
            self.db.add(audit)

        self.db.commit()
        self.db.refresh(case)
        return case
