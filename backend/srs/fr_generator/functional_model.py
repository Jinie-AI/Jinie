"""
functional_model.py

Domain-specific LLM layer for Stage 2 (Functional Requirements).
Mirrors requirement_model.py's pattern: knows nothing about HTTP —
only what prompt to send for FR generation, and how to parse the
response into a plain list-of-dicts shape that functional.py expects.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()


class ExtractedFR(TypedDict):
    description: str
    actors: List[str]
    inputs: List[str]
    outputs: List[str]
    priority: str  # "critical" | "high" | "medium" | "low"


_SYSTEM_PROMPT = """You are a Functional Requirements (FR) generation engine \
for a mobile app generation pipeline. Given a list of extracted keywords, \
intent tags, and the original app description, generate atomic, testable \
Functional Requirements.

Respond with ONLY a single valid JSON array, no markdown fences, no \
preamble, no explanation. Each array item must have exactly these keys:

{
  "description": "one clear sentence describing what the user can do",
  "actors": [list of actor roles, e.g. "AuthenticatedUser", "Guest", "Admin"],
  "inputs": [list of short snake_case input field names the action needs],
  "outputs": [list of short snake_case outputs/results the action produces],
  "priority": "critical" | "high" | "medium" | "low"
}

Generate between 3 and 10 FRs depending on how much the description \
implies. Each FR must be atomic (one action per FR, not compound). Do \
not invent features not implied by the text or keywords."""


def _build_user_prompt(normalized_text: str, keywords: List[str], intent_tags: List[str]) -> str:
    return (
        f"App description:\n\"\"\"\n{normalized_text}\n\"\"\"\n\n"
        f"Extracted keywords: {keywords}\n"
        f"Detected intent tags: {intent_tags}"
    )


def generate_frs_with_llm(
    normalized_text: str, keywords: List[str], intent_tags: List[str], trace_id: str
) -> Optional[List[ExtractedFR]]:
    """
    Calls the LLM to generate a list of Functional Requirements.
    Returns None (never raises) on any failure — caller falls back to
    the template-based archetype expansion in that case.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(normalized_text, keywords, intent_tags)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.3, max_tokens=1200)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | functional_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON array of FR objects")
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "trace_id=%s | functional_model.py | LLM response was not a valid JSON array | error=%s | raw=%s",
            trace_id, str(exc), cleaned[:300],
        )
        return None

    results: List[ExtractedFR] = []
    for index, item in enumerate(parsed):
        try:
            fr: ExtractedFR = {
                "description": str(item["description"]),
                "actors": [str(a) for a in item.get("actors", [])],
                "inputs": [str(i) for i in item.get("inputs", [])],
                "outputs": [str(o) for o in item.get("outputs", [])],
                "priority": str(item.get("priority", "medium")).lower(),
            }
            results.append(fr)
        except (KeyError, TypeError) as exc:
            logger.warning(
                "trace_id=%s | functional_model.py | skipping malformed FR item at index=%d | error=%s",
                trace_id, index, str(exc),
            )
            continue

    if not results:
        logger.warning("trace_id=%s | functional_model.py | LLM returned zero usable FRs", trace_id)
        return None

    logger.info(
        "trace_id=%s | functional_model.py | LLM generated %d FRs successfully",
        trace_id, len(results),
    )
    return results