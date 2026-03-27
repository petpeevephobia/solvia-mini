"""Google Custom Search JSON API (SERP)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


def search_google_cse(
    query: str,
    api_key: str,
    cx: str,
    timeout: float,
    num: int = 10,
) -> dict[str, Any]:
    if not api_key or not cx:
        raise ValueError("GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID must be set")
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": min(num, 10),
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.get(CSE_ENDPOINT, params=params)
        r.raise_for_status()
        return r.json()
