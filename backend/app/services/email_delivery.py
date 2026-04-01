"""Transactional email delivery via Zoho SMTP (stdlib smtplib, no extra deps)."""

from __future__ import annotations

import logging
import smtplib
import time
from email.message import EmailMessage
from typing import NamedTuple

from app.config import settings
from app.services.audit_email_template import build_audit_email

logger = logging.getLogger(__name__)

_RETRY_DELAY_SEC = 5.0


class EmailResult(NamedTuple):
    success: bool
    attempts: int
    error: str | None


def _require_smtp_config() -> None:
    """Raise ValueError if mandatory SMTP settings are absent."""
    missing: list[str] = []
    if not settings.smtp_host.strip():
        missing.append("SMTP_HOST")
    if not settings.smtp_username.strip():
        missing.append("SMTP_USERNAME")
    if not settings.smtp_password.strip():
        missing.append("SMTP_PASSWORD")
    if not settings.smtp_from_email.strip():
        missing.append("SMTP_FROM_EMAIL")
    if missing:
        raise ValueError(
            f"Missing SMTP configuration — set these env vars: {', '.join(missing)}"
        )


def _build_message(
    to_email: str,
    subject: str,
    html_body: str,
    plaintext_body: str,
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = (
        f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        if settings.smtp_from_name
        else settings.smtp_from_email
    )
    msg["To"] = to_email
    if settings.smtp_reply_to.strip():
        msg["Reply-To"] = settings.smtp_reply_to.strip()

    msg.set_content(plaintext_body)
    msg.add_alternative(html_body, subtype="html")
    return msg


def _attempt_send(msg: EmailMessage) -> None:
    """Open one SMTP connection, authenticate, and send."""
    if settings.smtp_use_tls:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)


def send_audit_email(
    to_email: str,
    audited_url: str,
    report_markdown: str,
) -> EmailResult:
    """
    Build and send the audit completion email.

    Attempts once, retries once on failure.
    Returns EmailResult with outcome details — never raises.
    """
    if not settings.smtp_configured:
        logger.warning(
            "SMTP not configured — skipping audit email to %s (audit url: %s)",
            to_email,
            audited_url,
        )
        return EmailResult(success=False, attempts=0, error="SMTP not configured")

    try:
        _require_smtp_config()
    except ValueError as exc:
        logger.error("SMTP config error: %s", exc)
        return EmailResult(success=False, attempts=0, error=str(exc))

    subject, html_body, plaintext_body = build_audit_email(report_markdown, audited_url)
    msg = _build_message(to_email, subject, html_body, plaintext_body)

    last_error: str | None = None
    for attempt in range(1, 3):  # attempt 1, then retry (attempt 2)
        try:
            _attempt_send(msg)
            logger.info(
                "Audit email delivered to=%s url=%s attempt=%d",
                to_email,
                audited_url,
                attempt,
            )
            return EmailResult(success=True, attempts=attempt, error=None)
        except smtplib.SMTPException as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            logger.warning(
                "SMTP send failed (attempt %d/2) to=%s: %s",
                attempt,
                to_email,
                last_error,
            )
            if attempt == 1:
                time.sleep(_RETRY_DELAY_SEC)
        except OSError as exc:
            last_error = f"Network error: {exc}"
            logger.warning(
                "SMTP network error (attempt %d/2) to=%s: %s",
                attempt,
                to_email,
                last_error,
            )
            if attempt == 1:
                time.sleep(_RETRY_DELAY_SEC)

    logger.error(
        "Audit email permanently failed after 2 attempts to=%s url=%s last_error=%s",
        to_email,
        audited_url,
        last_error,
    )
    return EmailResult(success=False, attempts=2, error=last_error)
