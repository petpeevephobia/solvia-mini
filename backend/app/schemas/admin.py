import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminAuditRow(BaseModel):
    id: uuid.UUID
    email: str
    url: str
    status: str
    error_message: str | None
    email_sent_at: datetime | None
    email_failed_at: datetime | None
    email_attempts: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminAuditDetail(AdminAuditRow):
    report_markdown: str | None
    page_audit_json: dict | list | None
    serp_analysis_json: dict | list | None
    email_error_message: str | None


class AdminAuditListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[AdminAuditRow]
