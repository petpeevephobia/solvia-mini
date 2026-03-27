"""Gemini text / JSON generation."""

from __future__ import annotations

import logging

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

_configured = False


def _ensure_configured() -> None:
    global _configured
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not set")
    if not _configured:
        genai.configure(api_key=settings.google_api_key)
        _configured = True


def get_model() -> genai.GenerativeModel:
    _ensure_configured()
    return genai.GenerativeModel(settings.gemini_model)


def _response_text(resp: object) -> str:
    text = getattr(resp, "text", None) or ""
    if text.strip():
        return text.strip()
    candidates = getattr(resp, "candidates", None) or []
    for c in candidates:
        content = getattr(c, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []) or []:
            t = getattr(part, "text", None)
            if t:
                text += t
    if not text.strip():
        raise RuntimeError("Gemini returned an empty response")
    return text.strip()


def generate_text(prompt: str) -> str:
    model = get_model()
    cfg = genai.GenerationConfig(
        max_output_tokens=settings.llm_max_output_tokens,
        temperature=0.3,
    )
    resp = model.generate_content(prompt, generation_config=cfg)
    return _response_text(resp)


def generate_json_text(prompt: str) -> str:
    """Ask model to return JSON (Gemini JSON mode when supported)."""
    model = get_model()
    try:
        cfg = genai.GenerationConfig(
            max_output_tokens=settings.llm_max_output_tokens,
            temperature=0.2,
            response_mime_type="application/json",
        )
        resp = model.generate_content(prompt, generation_config=cfg)
        return _response_text(resp)
    except Exception as e:
        logger.warning("JSON mode failed (%s), falling back to plain text", e)
        return generate_text(
            prompt
            + "\n\nRespond with ONLY valid JSON, no markdown fences or commentary."
        )
