"""Agent 1: deterministic base + Gemini keyword / intent."""

from __future__ import annotations

import json
import logging

from app.pipeline.extract import extract_from_html
from app.schemas.json_llm import parse_or_repair
from app.schemas.page_audit import PageAuditOutput
from app.services.firecrawl import ScrapePayload
from app.services.gemini import generate_json_text

logger = logging.getLogger(__name__)

_INTENTS = frozenset(
    {"informational", "commercial", "transactional", "navigational", "mixed", "unknown"}
)


def _repair(bad: str, err: str) -> str:
    return generate_json_text(
        "The JSON below failed validation. Return ONLY fixed valid JSON for the same object.\n"
        f"Error: {err}\n\nInvalid:\n{bad[:8000]}"
    )


def run_agent1(scrape: ScrapePayload, page_url: str) -> PageAuditOutput:
    base = extract_from_html(
        page_url,
        scrape.html,
        scrape.markdown,
        scrape.links,
        scrape.metadata,
    )
    schema_snippet = json.dumps(PageAuditOutput.model_json_schema(), indent=2)[:12000]
    prompt = (
        "You are an SEO analyst. Given the page audit JSON below, return ONE JSON object "
        "that matches the PageAuditOutput schema. Preserve internal_links, external_links, "
        "heading_counts, word_count, and technical measurements from the input; you may refine "
        "title, meta, primary_keyword, secondary_keywords (max 20), search_intent, and notes.\n\n"
        f"Input JSON:\n{base.model_dump_json(indent=2)[:14000]}\n\n"
        f"Schema (abridged):\n{schema_snippet}\n"
    )
    raw = generate_json_text(prompt)
    try:
        return parse_or_repair(PageAuditOutput, raw, _repair, "")
    except Exception as e:
        logger.warning("Agent1 full JSON failed (%s), falling back to base + minimal LLM", e)
        return _agent1_fallback_keywords(base)


def _agent1_fallback_keywords(base: PageAuditOutput) -> PageAuditOutput:
    mini = (
        "Return ONLY JSON: {\"primary_keyword\":\"\",\"secondary_keywords\":[],"
        '"search_intent":"unknown","notes":""} infer from title and headings.\n\n'
        f"Title: {base.title}\nHeadings: {base.heading_counts}\n"
    )
    raw = generate_json_text(mini)
    from app.schemas.json_llm import extract_json_object

    blob = extract_json_object(raw)
    data = json.loads(blob)
    si = data.get("search_intent") or "unknown"
    if si not in _INTENTS:
        si = "unknown"
    return base.model_copy(
        update={
            "primary_keyword": data.get("primary_keyword") or "general",
            "secondary_keywords": data.get("secondary_keywords") or [],
            "search_intent": si,
            "notes": data.get("notes"),
        }
    )


def build_page_audit_from_scrape(scrape: ScrapePayload, page_url: str) -> PageAuditOutput:
    """Public entry: scrape payload -> full PageAuditOutput."""
    return run_agent1(scrape, page_url)
