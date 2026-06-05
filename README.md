# Solvia MINI

A free SEO audit tool that tells founders exactly what's holding their website back in plain English, delivered to their email inbox.

## Why

Most founders treat their website like a business card. They ship it, move on, and wonder why organic traffic never comes. SEO feels like a dark art associated with expensive agencies, jargon-heavy reports, and fixes that need a developer.

Solvia is a first step toward making SEO human-friendly. You enter a URL, and within a couple of minutes you get a full audit in your inbox: what's broken, why it matters, and what to fix first.

## What it does

Solvia accepts a URL and email address, scrapes the page, runs it through three sequential AI agents, and delivers a prioritised Markdown report via email.

**Stack:** Python, FastAPI, Supabase (Postgres), Firecrawl (scraping), Gemini (LLM), Serper (SERP data), Zoho SMTP (email), Jekyll (frontend).

## Pipeline

**Agent 1 — Page audit**
Firecrawl scrapes the page (markdown, HTML, links). A deterministic pass extracts title, meta tags, heading structure, word count, internal/external links, and technical signals. Gemini then infers primary keyword, secondary keywords, and search intent to produce a validated `PageAuditOutput`.

**Agent 2 — SERP analysis**
The primary keyword from Agent 1 is passed to Serper's Google Search API. Gemini analyses the organic results, People Also Ask entries, answer boxes, and knowledge panels to produce a `SerpAnalysis` — patterns across top-ranking pages and concrete opportunities to exploit.

**Agent 3 — Report generation**
Both structured outputs feed into a final Gemini call that writes a prioritised Markdown report: executive summary, technical signals table, keyword and intent section, SERP landscape, and recommendations split into P0 / P1 / P2 with effort and impact ratings.

The report is then converted to HTML and delivered via transactional email (Zoho SMTP).

## Status lifecycle

The frontend polls the API every 3 seconds while the pipeline runs:

`queued` → `scraping` → `analyzing` → `generating` → `complete` | `failed`

## Secrets

```
DATABASE_URL
CORS_ORIGINS
FIRECRAWL_API_KEY
GOOGLE_API_KEY
GEMINI_MODEL
SERPER_API_KEY
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_FROM_NAME
SMTP_USE_TLS
SMTP_REPLY_TO
```

## On the horizon

- N/A

---

## Running Locally for Development

### Quick Start (Easiest Method)

1. **Install Jekyll** (see Jekyll Setup section below)
2. **Run Jekyll server**:
   ```bash
   bundle exec jekyll serve
   ```
3. **View site**: Open `http://localhost:4000`

> **Note**: For most development work (editing HTML, CSS, JavaScript), the simple Python server method is sufficient. Only use Jekyll if you're working on case study pages.

### Troubleshooting

- **Port already in use?** Change the port number (e.g., `8000` to `8001`)
- **Can't find Python?** Make sure Python is installed and added to your PATH
- **Files not updating?** Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)