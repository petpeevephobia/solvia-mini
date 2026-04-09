import csv
import io
import secrets
from datetime import datetime, timezone
from uuid import UUID

import markdown as md
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.limiter import limiter
from app.models import LeadAudit
from app.schemas.admin import AdminAuditDetail, AdminAuditListResponse, AdminAuditRow

router = APIRouter(tags=["admin"])

templates = Jinja2Templates(directory="app/templates")

_SESSION_COOKIE = "admin_session"
_SESSION_TTL_HOURS = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _signer() -> TimestampSigner:
    if not settings.admin_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured.",
        )
    return TimestampSigner(settings.admin_secret)


def _make_session_token() -> str:
    return _signer().sign("admin").decode()


def _verify_session_token(token: str) -> bool:
    try:
        _signer().unsign(token, max_age=_SESSION_TTL_HOURS * 3600)
        return True
    except (SignatureExpired, BadSignature):
        return False


# ---------------------------------------------------------------------------
# Auth dependencies
# ---------------------------------------------------------------------------


def verify_admin(request: Request) -> None:
    """Dependency for JSON API routes — checks X-Admin-Secret header."""
    if not settings.admin_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured.",
        )
    header = request.headers.get("x-admin-secret", "")
    if not secrets.compare_digest(header, settings.admin_secret):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret.",
        )


def verify_session(request: Request) -> None:
    """Dependency for HTML UI routes — checks signed session cookie."""
    token = request.cookies.get(_SESSION_COOKIE, "")
    if not token or not _verify_session_token(token):
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/admin/login"},
        )


# ---------------------------------------------------------------------------
# JSON API endpoints  (Day 1)
# ---------------------------------------------------------------------------


@router.get("/api/admin/audits", response_model=AdminAuditListResponse)
def list_audits(
    page: int = 1,
    limit: int = 50,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
) -> AdminAuditListResponse:
    limit = min(limit, 200)
    offset = (page - 1) * limit

    q = select(LeadAudit)
    count_q = select(func.count()).select_from(LeadAudit)
    if status_filter:
        q = q.where(LeadAudit.status == status_filter)
        count_q = count_q.where(LeadAudit.status == status_filter)

    q = q.order_by(LeadAudit.created_at.desc()).offset(offset).limit(limit)

    total = db.scalar(count_q) or 0
    rows = db.scalars(q).all()

    return AdminAuditListResponse(
        total=total,
        page=page,
        limit=limit,
        items=[AdminAuditRow.model_validate(r) for r in rows],
    )


@router.get("/api/admin/audits/export.csv")
def export_audits_csv(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
) -> StreamingResponse:
    rows = db.scalars(select(LeadAudit).order_by(LeadAudit.created_at.desc())).all()

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "id",
                "email",
                "url",
                "status",
                "error_message",
                "email_sent_at",
                "email_failed_at",
                "email_attempts",
                "created_at",
                "updated_at",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.id,
                    r.email,
                    r.url,
                    r.status,
                    r.error_message or "",
                    r.email_sent_at or "",
                    r.email_failed_at or "",
                    r.email_attempts,
                    r.created_at,
                    r.updated_at,
                ]
            )
        yield buf.getvalue()

    filename = f"leads_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/api/admin/audits/{audit_id}", response_model=AdminAuditDetail)
def get_audit_detail(
    audit_id: UUID,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
) -> AdminAuditDetail:
    row = db.get(LeadAudit, audit_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
    return AdminAuditDetail.model_validate(row)


# ---------------------------------------------------------------------------
# HTML UI endpoints  (Day 2)
# ---------------------------------------------------------------------------


@router.get("/admin/export.csv")
def export_audits_csv_session(
    db: Session = Depends(get_db),
    _: None = Depends(verify_session),
) -> StreamingResponse:
    """Session-authenticated CSV export for browser UI."""
    rows = db.scalars(select(LeadAudit).order_by(LeadAudit.created_at.desc())).all()

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "id",
                "email",
                "url",
                "status",
                "error_message",
                "email_sent_at",
                "email_failed_at",
                "email_attempts",
                "created_at",
                "updated_at",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.id,
                    r.email,
                    r.url,
                    r.status,
                    r.error_message or "",
                    r.email_sent_at or "",
                    r.email_failed_at or "",
                    r.email_attempts,
                    r.created_at,
                    r.updated_at,
                ]
            )
        yield buf.getvalue()

    filename = f"leads_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/admin/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"error": None})


@router.post("/admin/login", response_class=HTMLResponse, response_model=None)
@limiter.limit("5/minute")
async def login_submit(
    request: Request,
    secret: str = Form(...),
) -> HTMLResponse | RedirectResponse:
    if not settings.admin_secret:
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={"error": "Admin access is not configured."},
            status_code=503,
        )
    if not secrets.compare_digest(secret, settings.admin_secret):
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={"error": "Incorrect secret. Try again."},
            status_code=401,
        )
    token = _make_session_token()
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=_SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.cors_origins.startswith("http://localhost"),
        max_age=_SESSION_TTL_HOURS * 3600,
    )
    return response


@router.post("/admin/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(_SESSION_COOKIE)
    return response


@router.get("/admin", response_class=HTMLResponse)
def admin_list(
    request: Request,
    page: int = 1,
    limit: int = 50,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(verify_session),
) -> HTMLResponse:
    limit = min(limit, 200)
    offset = (page - 1) * limit

    q = select(LeadAudit)
    count_q = select(func.count()).select_from(LeadAudit)
    if status_filter:
        q = q.where(LeadAudit.status == status_filter)
        count_q = count_q.where(LeadAudit.status == status_filter)

    q = q.order_by(LeadAudit.created_at.desc()).offset(offset).limit(limit)
    total = db.scalar(count_q) or 0
    rows = db.scalars(q).all()

    # summary stats (always full table, not filtered)
    stats_q = select(LeadAudit.status, func.count().label("n")).group_by(LeadAudit.status)
    stats_raw = db.execute(stats_q).all()
    stats = {row.status: row.n for row in stats_raw}
    total_all = sum(stats.values())

    total_pages = max(1, (total + limit - 1) // limit)

    return templates.TemplateResponse(
        request=request,
        name="admin/list.html",
        context={
            "rows": rows,
            "total": total,
            "total_all": total_all,
            "stats": stats,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "status_filter": status_filter or "",
        },
    )


@router.get("/admin/{audit_id}", response_class=HTMLResponse)
def admin_detail(
    audit_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_session),
) -> HTMLResponse:
    row = db.get(LeadAudit, audit_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")

    report_html = md.markdown(row.report_markdown or "", extensions=["tables", "fenced_code"]) if row.report_markdown else None

    return templates.TemplateResponse(
        request=request,
        name="admin/detail.html",
        context={"row": row, "report_html": report_html},
    )
