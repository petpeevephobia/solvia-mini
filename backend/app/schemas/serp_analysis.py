from __future__ import annotations

from pydantic import BaseModel, Field


class SerpResultItem(BaseModel):
    rank: int = Field(ge=1)
    title: str = ""
    url: str = ""
    snippet: str | None = None


class SerpAnalysis(BaseModel):
    """SERP + competitive signals derived from Google CSE + LLM."""

    primary_keyword: str = ""
    serp_results: list[SerpResultItem] = Field(default_factory=list)
    patterns: str = ""
    people_also_ask: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    provider_metadata: dict[str, str] = Field(default_factory=dict)
