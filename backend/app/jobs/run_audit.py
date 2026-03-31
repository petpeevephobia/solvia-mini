"""Full audit pipeline: Firecrawl → Agent 1 → Serper → Agent 2 → Agent 3."""

from __future__ import annotations

import logging
import uuid

from app.config import settings
from app.db import SessionLocal
from app.models import LeadAudit
from app.pipeline.agent1 import run_agent1
from app.pipeline.agent2 import run_agent2
from app.pipeline.agent3 import run_agent3
from app.services.firecrawl import scrape_page
from app.services.serp import search_serper

logger = logging.getLogger(__name__)


def _require_pipeline_env() -> None:
    missing: list[str] = []
    if not settings.firecrawl_api_key.strip():
        missing.append("FIRECRAWL_API_KEY")
    if not settings.google_api_key.strip():
        missing.append("GOOGLE_API_KEY")
    if not settings.serper_api_key.strip():
        missing.append("SERPER_API_KEY")
    if missing:
        raise ValueError(f"Missing or empty environment variables: {', '.join(missing)}")


def _fail(db, row: LeadAudit | None, msg: str) -> None:
    if row is None:
        return
    try:
        row.status = "failed"
        row.error_message = msg[:2000]
        db.commit()
    except Exception:
        logger.exception("could not persist failure status")


def run_audit_pipeline(audit_id: uuid.UUID) -> None:
    _require_pipeline_env()
    db = SessionLocal()
    row: LeadAudit | None = None
    try:
        row = db.get(LeadAudit, audit_id)
        if row is None:
            logger.warning("lead_audit %s not found", audit_id)
            return

        row.status = "scraping"
        row.error_message = None
        db.commit()

        scrape = scrape_page(
            row.url,
            settings.firecrawl_api_key,
            settings.scrape_timeout_sec,
        )

        row.status = "analyzing"
        db.commit()

        page = run_agent1(scrape, row.url)
        row.page_audit_json = page.model_dump(mode="json")
        db.commit()

        keyword = (page.primary_keyword or "").strip() or (page.title or "page")[:120]
        raw_serp = search_serper(
            keyword,
            settings.serper_api_key,
            settings.serp_timeout_sec,
        )
        serp = run_agent2(raw_serp, keyword)
        row.serp_analysis_json = serp.model_dump(mode="json")
        db.commit()

        row.status = "generating"
        db.commit()

        report = run_agent3(page, serp)
        row.report_markdown = report
        row.status = "complete"
        db.commit()
    except Exception as e:
        logger.exception("audit pipeline failed for %s", audit_id)
        _fail(db, row, str(e))
    finally:
        db.close()
