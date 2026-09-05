"""Reports API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from apps.backend.app.db.session import get_db
from apps.backend.app.api.deps import get_current_active_user, require_case_access
from apps.backend.app.models.user import User
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
from apps.backend.app.services.report import ReportService
from apps.backend.app.services.audit import log_action, REPORT_EXPORTED

router = APIRouter()


@router.get(
    "/html",
    response_class=HTMLResponse,
    summary="Export case evidence-backed report as HTML",
    responses={
        200: {
            "description": "HTML report file",
            "content": {"text/html": {}},
        }
    }
)
def export_html_report(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    access: CaseAccess = Depends(require_case_access(CaseAccessLevel.VIEW)),
):
    """
    Generate and export an evidence-backed HTML report for the case.
    Requires VIEW access to the case.
    """
    service = ReportService(db)
    
    try:
        html_content, metadata = service.generate_html_report(case_id, current_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except Exception as exc:
        # Do not log raw case data or template contents on failure
        # Safe error masking
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report due to an internal error."
        )

    # Log successful export exactly once
    log_action(
        db=db,
        action=REPORT_EXPORTED,
        target_type="CASE",
        target_id=case_id,
        user_id=current_user.id,
        rationale="Exported HTML case report",
        new_state=metadata  # Only safe counts and versions
    )

    # Construct safe filename (just case_id to prevent injection)
    safe_filename = f"case-report-{case_id}.html"

    # Return securely configured response
    return HTMLResponse(
        content=html_content,
        headers={
            "Content-Type": "text/html; charset=utf-8",
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store",
        }
    )
