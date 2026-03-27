"""Agent 2: Google CSE results + Gemini synthesis."""

from __future__ import annotations

import json
import logging

from app.schemas.json_llm import extract_json_object
from app.schemas.serp_analysis import SerpAnalysis, SerpResultItem
from app.services.gemini import generate_json_text

logger = logging.getLogger(__name__)


def serp_results_from_api(raw: dict) -> list[SerpResultItem]:
    items: list[SerpResultItem] = []
    for i, it in enumerate(raw.get("items") or [], start=1):
        items.append(
            SerpResultItem(
                rank=i,
                title=(it.get("title") or "")[:500],
                url=(it.get("link") or "")[:2000],
                snippet=(it.get("snippet") or it.get("htmlSnippet") or "")[:800],
            )
        )
    return items


def run_agent2(raw_serp: dict, primary_keyword: str) -> SerpAnalysis:
    results = serp_results_from_api(raw_serp)
    prompt = (
        "You are an SEO strategist. Given the search keyword and organic SERP results, "
        "produce analysis JSON with exactly these keys:\n"
        '- "patterns": string summarizing dominant SERP patterns (titles, intent mix).\n'
        '- "people_also_ask": array of strings (use related questions if present in context; else [].\n'
        '- "opportunities": array of concrete SEO opportunities for a page targeting this keyword.\n'
        '- "provider_metadata": object with string values only (e.g. total_results estimate as string).\n\n'
        f"Keyword: {primary_keyword}\n"
        f"Raw CSE snippet:\n{json.dumps(raw_serp)[:10000]}\n"
    )
    raw = generate_json_text(prompt)
    try:
        blob = extract_json_object(raw)
        data = json.loads(blob)
        return SerpAnalysis(
            primary_keyword=primary_keyword,
            serp_results=results,
            patterns=str(data.get("patterns") or ""),
            people_also_ask=list(data.get("people_also_ask") or []),
            opportunities=list(data.get("opportunities") or []),
            provider_metadata={
                str(k): str(v)
                for k, v in (data.get("provider_metadata") or {}).items()
                if v is not None
            },
        )
    except Exception as e:
        logger.warning("Agent2 parse failed (%s), using minimal SerpAnalysis", e)
        return SerpAnalysis(
            primary_keyword=primary_keyword,
            serp_results=results,
            patterns="SERP results retrieved; see serp_results for competitors.",
            opportunities=["Differentiate title and meta vs top results."],
        )
