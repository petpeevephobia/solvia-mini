from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LinkStats(BaseModel):
    count: int = Field(ge=0)
    sample_urls: list[str] = Field(default_factory=list, max_length=20)


class PageMeta(BaseModel):
    description: str | None = None
    canonical: str | None = None
    robots: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    twitter_card: str | None = None


class PageTechnical(BaseModel):
    viewport: str | None = None
    charset: str | None = None
    html_lang: str | None = None
    has_https: bool = True


class PageAuditOutput(BaseModel):
    """Structured page audit after scrape + extraction + LLM enrichment."""

    url: str
    title: str | None = None
    meta: PageMeta = Field(default_factory=PageMeta)
    heading_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Counts per tag, keys like h1, h2, ...",
    )
    word_count: int = Field(ge=0, default=0)
    internal_links: LinkStats = Field(default_factory=lambda: LinkStats(count=0))
    external_links: LinkStats = Field(default_factory=lambda: LinkStats(count=0))
    technical: PageTechnical = Field(default_factory=PageTechnical)
    primary_keyword: str = ""
    secondary_keywords: list[str] = Field(default_factory=list, max_length=20)
    search_intent: Literal[
        "informational",
        "commercial",
        "transactional",
        "navigational",
        "mixed",
        "unknown",
    ] = "unknown"
    notes: str | None = None
