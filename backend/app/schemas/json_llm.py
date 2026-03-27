"""Parse and optionally repair LLM JSON output against a Pydantic model."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def extract_json_object(text: str) -> str:
    """Strip markdown fences and return the first JSON object substring."""
    t = text.strip()
    fence = re.match(r"^```(?:json)?\s*([\s\S]*?)```$", t, re.IGNORECASE)
    if fence:
        t = fence.group(1).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start >= 0 and end > start:
        return t[start : end + 1]
    return t


def parse_model(model: type[T], raw: str) -> T:
    blob = extract_json_object(raw)
    data = json.loads(blob)
    return model.model_validate(data)


def parse_or_repair(
    model: type[T],
    raw: str,
    repair: Callable[[str, str], str],
    schema_hint: str,
) -> T:
    """Try strict parse; on ValidationError call repair(invalid_json, errors) once."""
    blob = extract_json_object(raw)
    try:
        return model.model_validate(json.loads(blob))
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("JSON parse failed, attempting repair: %s", e)
        fixed = repair(blob, str(e)[:500])
        return parse_model(model, fixed)
