from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.jobs.run_audit import run_audit_pipeline
from app.models import LeadAudit
from app.schemas.audit import AuditAccepted, AuditCreate, AuditStatusResponse

router = APIRouter(tags=["audit"])


@router.post(
    "/audit",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuditAccepted,
)
def create_audit(
    body: AuditCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> AuditAccepted:
    audit = LeadAudit(
        url=body.url,
        email=body.email.lower().strip(),
        status="queued",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    background_tasks.add_task(run_audit_pipeline, audit.id)
    return AuditAccepted(audit_id=audit.id, status="queued")


@router.get("/audit/{audit_id}/status", response_model=AuditStatusResponse)
def get_audit_status(
    audit_id: UUID,
    db: Session = Depends(get_db),
) -> AuditStatusResponse:
    row = db.get(LeadAudit, audit_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
    return AuditStatusResponse(
        audit_id=row.id,
        status=row.status,
        error_message=row.error_message,
        email_sent_at=row.email_sent_at,
        email_failed_at=row.email_failed_at,
        email_attempts=row.email_attempts,
    )
