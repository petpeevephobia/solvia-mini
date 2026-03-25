import logging
import time
import uuid

from app.db import SessionLocal
from app.models import LeadAudit

logger = logging.getLogger(__name__)

_STUB_SEQUENCE = ("scraping", "analyzing", "generating", "complete")
_STUB_DELAY_SEC = 0.8


def run_audit_stub(audit_id: uuid.UUID) -> None:
    """Simulate the multi-agent pipeline by stepping status in the database."""
    db = SessionLocal()
    try:
        for status in _STUB_SEQUENCE:
            time.sleep(_STUB_DELAY_SEC)
            row = db.get(LeadAudit, audit_id)
            if row is None:
                logger.warning("lead_audit %s not found, stopping stub", audit_id)
                return
            row.status = status
            db.commit()
    except Exception as e:
        logger.exception("audit stub failed for %s", audit_id)
        try:
            row = db.get(LeadAudit, audit_id)
            if row is not None:
                row.status = "failed"
                row.error_message = str(e)[:2000]
                db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()
