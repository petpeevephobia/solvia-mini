"""Serper.dev Google Search API client.

POST https://google.serper.dev/search
Auth: X-API-KEY header

Response shape (relevant fields):
  organic:        [{position, title, link, snippet, sitelinks?, date?, attributes?}]
  peopleAlsoAsk:  [{question, snippet, title, link}]
  relatedSearches:[{query}]
  answerBox:      {title?, snippet?, snippetHighlighted?, link?}
  knowledgeGraph: {title?, type?, description?, website?, attributes?}
  searchParameters: {q, gl, hl, type, num}
  credits:        int
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

SERPER_ENDPOINT = "https://google.serper.dev/search"


def search_serper(
    query: str,
    api_key: str,
    timeout: float,
    num: int = 10,
    gl: str = "us",
    hl: str = "en",
) -> dict[str, Any]:
    """Execute a Google search via Serper.dev and return the raw response dict."""
    if not api_key:
        raise ValueError("SERPER_API_KEY must be set")

    payload: dict[str, Any] = {"q": query, "num": min(num, 10), "gl": gl, "hl": hl}
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=timeout) as client:
        r = client.post(SERPER_ENDPOINT, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
