from __future__ import annotations

from pydantic import BaseModel, Field


class SerpResultItem(BaseModel):
    rank: int = Field(ge=1)
    title: str = ""
    url: str = ""
    snippet: str | None = None
    date: str | None = None  # Serper may include a result date


class PeopleAlsoAskItem(BaseModel):
    """A single PAA entry from Serper — includes the source snippet and URL."""

    question: str = ""
    snippet: str | None = None
    title: str | None = None
    link: str | None = None


class AnswerBox(BaseModel):
    """Featured snippet / answer box returned by Serper when present."""

    title: str | None = None
    snippet: str | None = None
    snippet_highlighted: list[str] = Field(default_factory=list)
    link: str | None = None


class KnowledgeGraph(BaseModel):
    """Entity card returned by Serper when the query has a knowledge panel."""

    title: str | None = None
    type: str | None = None
    description: str | None = None
    website: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class SerpAnalysis(BaseModel):
    """SERP + competitive signals derived from Serper.dev + LLM."""

    primary_keyword: str = ""
    serp_results: list[SerpResultItem] = Field(default_factory=list)

    # Serper-native rich SERP features
    people_also_ask: list[PeopleAlsoAskItem] = Field(default_factory=list)
    related_searches: list[str] = Field(default_factory=list)
    answer_box: AnswerBox | None = None
    knowledge_graph: KnowledgeGraph | None = None

    # LLM-derived
    patterns: str = ""
    opportunities: list[str] = Field(default_factory=list)
    provider_metadata: dict[str, str] = Field(default_factory=dict)
