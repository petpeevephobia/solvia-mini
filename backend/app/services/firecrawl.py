"""Firecrawl scrape via HTTP API (markdown, html, links)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v1/scrape"


@dataclass
class ScrapePayload:
    markdown: str
    html: str
    links: list[str]
    metadata: dict[str, Any]
    source_url: str | None


def _normalize_links(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict) and "url" in item:
                out.append(str(item["url"]))
        return out
    return []


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    reraise=True,
)
def _post_scrape(url: str, api_key: str, timeout: float) -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        r = client.post(
            FIRECRAWL_SCRAPE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "url": url,
                "formats": ["markdown", "html", "links"],
            },
        )
        r.raise_for_status()
        return r.json()


def scrape_page(url: str, api_key: str, timeout: float) -> ScrapePayload:
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY is not set")
    body = _post_scrape(url, api_key, timeout)
    if not body.get("success"):
        err = body.get("error", body)
        logger.error("Firecrawl error: %s", err)
        raise RuntimeError(f"Firecrawl scrape failed: {err}")
    data = body.get("data") or {}
    md = data.get("markdown") or ""
    html = data.get("html") or ""
    links = _normalize_links(data.get("links"))
    meta = data.get("metadata") or {}
    if isinstance(meta, dict):
        meta_dict: dict[str, Any] = dict(meta)
    else:
        meta_dict = {}
    src = meta_dict.get("sourceURL") or meta_dict.get("url") or url
    return ScrapePayload(
        markdown=md,
        html=html,
        links=links,
        metadata=meta_dict,
        source_url=str(src) if src else None,
    )
