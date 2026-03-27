"""Deterministic signals from HTML / markdown / link list."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.schemas.page_audit import LinkStats, PageMeta, PageTechnical, PageAuditOutput


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}".lower()


def classify_links(page_url: str, hrefs: list[str]) -> tuple[list[str], list[str]]:
    base = urlparse(page_url)
    netloc = base.netloc.lower()
    internal: list[str] = []
    external: list[str] = []
    for h in hrefs:
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(page_url, h.strip())
        p = urlparse(full)
        if not p.netloc:
            internal.append(full)
        elif p.netloc.lower() == netloc:
            internal.append(full)
        else:
            external.append(full)
    return internal, external


def word_count_from_markdown(md: str) -> int:
    text = re.sub(r"[#*_`\[\]()]", " ", md)
    return len([w for w in text.split() if w.strip()])


def extract_from_html(
    page_url: str,
    html: str,
    markdown: str,
    link_hrefs: list[str],
    metadata: dict,
) -> PageAuditOutput:
    soup = BeautifulSoup(html or "", "html.parser")
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title and metadata.get("title"):
        title = str(metadata["title"]).strip()

    meta = PageMeta()
    for tag in soup.find_all("meta"):
        name = (tag.get("name") or tag.get("property") or "").lower()
        content = tag.get("content")
        if not content:
            continue
        if name == "description":
            meta.description = content
        elif name == "robots":
            meta.robots = content
        elif name in ("og:title",):
            meta.og_title = content
        elif name in ("og:description",):
            meta.og_description = content
        elif name in ("twitter:card",):
            meta.twitter_card = content
    link_el = soup.find("link", rel=lambda x: x and "canonical" in str(x).lower())
    if link_el and link_el.get("href"):
        meta.canonical = str(link_el["href"]).strip()

    counts: dict[str, int] = {}
    for level in range(1, 7):
        tag = f"h{level}"
        n = len(soup.find_all(tag))
        if n:
            counts[tag] = n

    wc = word_count_from_markdown(markdown) if markdown else len(
        (soup.get_text() or "").split()
    )

    internal, external = classify_links(page_url, link_hrefs)
    html_el = soup.find("html")
    tech = PageTechnical(
        html_lang=(html_el.get("lang") if html_el else None),
        charset=None,
        viewport=None,
        has_https=urlparse(page_url).scheme == "https",
    )
    v = soup.find("meta", attrs={"name": "viewport"})
    if v and v.get("content"):
        tech.viewport = v["content"]
    cset = soup.find("meta", attrs={"charset": True})
    if cset:
        tech.charset = cset.get("charset")

    return PageAuditOutput(
        url=page_url,
        title=title,
        meta=meta,
        heading_counts=counts,
        word_count=wc,
        internal_links=LinkStats(
            count=len(internal),
            sample_urls=internal[:15],
        ),
        external_links=LinkStats(
            count=len(external),
            sample_urls=external[:15],
        ),
        technical=tech,
    )
