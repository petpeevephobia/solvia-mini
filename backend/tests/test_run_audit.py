"""Orchestration tests with external APIs mocked."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.pipeline.extract import extract_from_html
from app.schemas.page_audit import LinkStats, PageAuditOutput, PageTechnical
from app.schemas.serp_analysis import SerpAnalysis
from app.services.firecrawl import ScrapePayload


@pytest.fixture
def sample_page() -> PageAuditOutput:
    return PageAuditOutput(
        url="https://example.com/page",
        title="Example",
        word_count=10,
        internal_links=LinkStats(count=1, sample_urls=["https://example.com/a"]),
        external_links=LinkStats(count=0),
        primary_keyword="example",
        technical=PageTechnical(),
    )


def test_extract_from_html_basic():
    html = """<html lang="en"><head>
    <title>Hello</title>
    <meta name="description" content="Desc">
    <meta charset="utf-8">
    </head><body>
    <h1>Main</h1><h2>Sub</h2>
    <a href="/int">in</a><a href="https://other.com/x">out</a>
    </body></html>"""
    out = extract_from_html(
        "https://example.com/",
        html,
        "# Hello\nworld",
        ["/int", "https://other.com/x"],
        {},
    )
    assert out.title == "Hello"
    assert out.word_count >= 2
    assert out.heading_counts.get("h1") == 1
    assert out.internal_links.count >= 1
    assert out.external_links.count >= 1


@patch("app.jobs.run_audit.run_agent3", return_value="# Audit\nDone")
@patch("app.jobs.run_audit.run_agent2")
@patch("app.jobs.run_audit.search_google_cse", return_value={"items": []})
@patch("app.jobs.run_audit.run_agent1")
@patch("app.jobs.run_audit.scrape_page")
@patch("app.jobs.run_audit._require_pipeline_env")
def test_run_audit_pipeline_happy_path(
    _req,
    mock_scrape,
    mock_a1,
    _cse,
    mock_a2,
    _a3,
    sample_page: PageAuditOutput,
):
    mock_scrape.return_value = ScrapePayload(
        markdown="# x",
        html="<html><title>T</title></html>",
        links=[],
        metadata={},
        source_url="https://example.com/page",
    )
    mock_a1.return_value = sample_page
    mock_a2.return_value = SerpAnalysis(primary_keyword="example", serp_results=[])

    audit_id = uuid.uuid4()

    class Row:
        def __init__(self) -> None:
            self.id = audit_id
            self.url = "https://example.com/page"
            self.status = "queued"
            self.error_message = None
            self.page_audit_json = None
            self.serp_analysis_json = None
            self.report_markdown = None

    row = Row()
    db = MagicMock()

    def _get(_model, _id):
        return row if _id == audit_id else None

    db.get.side_effect = _get

    with patch("app.jobs.run_audit.SessionLocal", return_value=db):
        from app.jobs.run_audit import run_audit_pipeline

        run_audit_pipeline(audit_id)

    assert row.status == "complete"
    assert row.report_markdown == "# Audit\nDone"
    assert row.page_audit_json is not None
    assert row.serp_analysis_json is not None
    db.close.assert_called_once()
