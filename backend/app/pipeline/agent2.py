"""Agent 2: Serper SERP results + Gemini synthesis.

Parses the Serper.dev JSON response shape:
  organic        → SerpResultItem list
  peopleAlsoAsk  → PeopleAlsoAskItem list (question + snippet + source)
  relatedSearches→ list[str]
  answerBox      → AnswerBox (featured snippet)
  knowledgeGraph → KnowledgeGraph (entity card)
"""

from __future__ import annotations

import json
import logging

from app.schemas.json_llm import extract_json_object
from app.schemas.serp_analysis import (
    AnswerBox,
    KnowledgeGraph,
    PeopleAlsoAskItem,
    SerpAnalysis,
    SerpResultItem,
)
from app.services.gemini import generate_json_text

logger = logging.getLogger(__name__)


# ── Raw-response parsers ──────────────────────────────────────────────────────

def _parse_organic(raw: dict) -> list[SerpResultItem]:
    items: list[SerpResultItem] = []
    for it in raw.get("organic") or []:
        items.append(
            SerpResultItem(
                rank=int(it.get("position") or len(items) + 1),
                title=(it.get("title") or "")[:500],
                url=(it.get("link") or "")[:2000],
                snippet=(it.get("snippet") or "")[:800],
                date=it.get("date"),
            )
        )
    return items


def _parse_paa(raw: dict) -> list[PeopleAlsoAskItem]:
    result: list[PeopleAlsoAskItem] = []
    for item in raw.get("peopleAlsoAsk") or []:
        result.append(
            PeopleAlsoAskItem(
                question=(item.get("question") or "")[:500],
                snippet=(item.get("snippet") or "")[:800] or None,
                title=(item.get("title") or "") or None,
                link=(item.get("link") or "") or None,
            )
        )
    return result


def _parse_related_searches(raw: dict) -> list[str]:
    return [
        (r.get("query") or "")[:300]
        for r in (raw.get("relatedSearches") or [])
        if r.get("query")
    ]


def _parse_answer_box(raw: dict) -> AnswerBox | None:
    ab = raw.get("answerBox")
    if not ab:
        return None
    return AnswerBox(
        title=(ab.get("title") or "") or None,
        snippet=(ab.get("snippet") or "") or None,
        snippet_highlighted=list(ab.get("snippetHighlighted") or []),
        link=(ab.get("link") or "") or None,
    )


def _parse_knowledge_graph(raw: dict) -> KnowledgeGraph | None:
    kg = raw.get("knowledgeGraph")
    if not kg:
        return None
    return KnowledgeGraph(
        title=(kg.get("title") or "") or None,
        type=(kg.get("type") or "") or None,
        description=(kg.get("description") or "") or None,
        website=(kg.get("website") or "") or None,
        attributes={
            str(k): str(v)
            for k, v in (kg.get("attributes") or {}).items()
            if v is not None
        },
    )


# ── Main agent entry point ────────────────────────────────────────────────────

def run_agent2(raw_serp: dict, primary_keyword: str) -> SerpAnalysis:
    organic = _parse_organic(raw_serp)
    paa = _parse_paa(raw_serp)
    related = _parse_related_searches(raw_serp)
    answer_box = _parse_answer_box(raw_serp)
    knowledge_graph = _parse_knowledge_graph(raw_serp)

    # Build a compact SERP summary for the LLM (stay within token budget)
    serp_summary = {
        "organic": [
            {"position": r.rank, "title": r.title, "url": r.url, "snippet": r.snippet}
            for r in organic
        ],
        "peopleAlsoAsk": [{"question": p.question, "snippet": p.snippet} for p in paa],
        "relatedSearches": related,
        "answerBox": (
            {"title": answer_box.title, "snippet": answer_box.snippet}
            if answer_box
            else None
        ),
        "knowledgeGraph": (
            {"title": knowledge_graph.title, "description": knowledge_graph.description}
            if knowledge_graph
            else None
        ),
        "searchParameters": raw_serp.get("searchParameters", {}),
    }

    prompt = (
        "You are an SEO strategist. Given the keyword and Serper SERP data below, "
        "produce a JSON object with exactly these keys:\n"
        '- "patterns": string — summarise dominant SERP patterns (title styles, '
        "content formats, search intent mix, featured snippets).\n"
        '- "opportunities": array of strings — concrete, actionable SEO opportunities '
        "a page targeting this keyword can exploit (gap vs competitors, PAA angles, "
        "answer-box potential, etc.).\n"
        '- "provider_metadata": object with string values only '
        "(e.g. total_results, answer_box_present, knowledge_graph_present).\n\n"
        f"Keyword: {primary_keyword}\n\n"
        f"SERP data (Serper.dev):\n{json.dumps(serp_summary)[:10000]}\n"
    )

    raw_llm = generate_json_text(prompt)
    try:
        blob = extract_json_object(raw_llm)
        data = json.loads(blob)
        return SerpAnalysis(
            primary_keyword=primary_keyword,
            serp_results=organic,
            people_also_ask=paa,
            related_searches=related,
            answer_box=answer_box,
            knowledge_graph=knowledge_graph,
            patterns=str(data.get("patterns") or ""),
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
            serp_results=organic,
            people_also_ask=paa,
            related_searches=related,
            answer_box=answer_box,
            knowledge_graph=knowledge_graph,
            patterns="SERP results retrieved; see serp_results for competitors.",
            opportunities=["Differentiate title and meta vs top results."],
        )
