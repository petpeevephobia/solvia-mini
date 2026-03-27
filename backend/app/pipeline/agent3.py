"""Agent 3: Markdown report from structured JSON."""

from __future__ import annotations

from app.schemas.page_audit import PageAuditOutput
from app.schemas.serp_analysis import SerpAnalysis
from app.services.gemini import generate_text


def run_agent3(page: PageAuditOutput, serp: SerpAnalysis) -> str:
    prompt = (
        "You are an SEO consultant. Write a concise audit report in **Markdown only** "
        "(no HTML). Use this structure:\n\n"
        "## Executive summary\n"
        "## Technical signals\n"
        "Use a Markdown table: | Signal | Detail |\n"
        "## Keyword & search intent\n"
        "## SERP & competitive landscape\n"
        "## Recommendations\n"
        "Subsections ### P0 (critical), ### P1 (important), ### P2 (nice to have). "
        "For each item include **Effort**: Low/Medium/High and **Impact**: Low/Medium/High.\n\n"
        "Data — Page audit:\n```json\n"
        f"{page.model_dump_json(indent=2)[:14000]}\n```\n\n"
        "Data — SERP analysis:\n```json\n"
        f"{serp.model_dump_json(indent=2)[:14000]}\n```\n"
    )
    return generate_text(prompt)
