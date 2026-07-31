"""
non_functional_model.py

Domain-specific LLM layer for Stage 3 (Non-Functional Requirements).
Given the generated FR list, asks the LLM to attach realistic quality
constraints (performance, security, reliability, etc) linked back to
specific fr_ids, instead of relying only on the fixed keyword-trigger
table in non_functional.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()

_VALID_CATEGORIES = {
    "performance", "security", "usability", "reliability", "scalability", "accessibility",
}


class ExtractedNFR(TypedDict):
    category: str
    constraint: str
    linked_fr_id: Optional[str]
    threshold_value: Optional[float]
    threshold_unit: Optional[str]


_SYSTEM_PROMPT = """You are a Non-Functional Requirements (NFR) generation \
engine for a mobile app generation pipeline. Given a list of Functional \
Requirements (each with an fr_id and description), generate realistic \
quality constraints: performance envelopes, security bounds, reliability, \
scalability, usability, or accessibility requirements. Each NFR should be \
linked to the specific fr_id it governs where relevant.

Respond with ONLY a single valid JSON array, no markdown fences, no \
preamble, no explanation. Each array item must have exactly these keys:

{
  "category": "performance" | "security" | "usability" | "reliability" | \
"scalability" | "accessibility",
  "constraint": "one clear sentence stating the constraint",
  "linked_fr_id": the fr_id string this constraint applies to, or null if \
it applies globally,
  "threshold_value": a number if the constraint has a measurable \
threshold (e.g. 200 for '200ms'), otherwise null,
  "threshold_unit": a short unit string (e.g. "ms", "%", "s"), or null
}

Generate one NFR per FR at minimum for critical/high priority FRs, plus \
any additional global NFRs you judge necessary. Do not invent FRs that \
were not given to you — only reference fr_ids from the input list."""


def _build_user_prompt(fr_summaries: List[dict]) -> str:
    lines = [f"- {fr['fr_id']}: {fr['description']} (priority: {fr['priority']})" for fr in fr_summaries]
    return "Functional Requirements:\n" + "\n".join(lines)


def generate_nfrs_with_llm(fr_summaries: List[dict], trace_id: str) -> Optional[List[ExtractedNFR]]:
    """
    Calls the LLM to generate NFRs linked to the given FR summaries.
    `fr_summaries` is a list of plain dicts: [{"fr_id": ..., "description": ..., "priority": ...}, ...]

    Returns None (never raises) on any failure — caller falls back to
    the keyword-trigger baseline logic in non_functional.py.
    """
    if not fr_summaries:
        logger.debug("trace_id=%s | non_functional_model.py | no FRs provided, skipping LLM call", trace_id)
        return None

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(fr_summaries)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.3, max_tokens=1200)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | non_functional_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON array of NFR objects")
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "trace_id=%s | non_functional_model.py | LLM response was not a valid JSON array | error=%s | raw=%s",
            trace_id, str(exc), cleaned[:300],
        )
        return None

    valid_fr_ids = {fr["fr_id"] for fr in fr_summaries}
    results: List[ExtractedNFR] = []

    for index, item in enumerate(parsed):
        try:
            category = str(item["category"]).lower()
            if category not in _VALID_CATEGORIES:
                logger.debug(
                    "trace_id=%s | non_functional_model.py | skipping NFR at index=%d, invalid category='%s'",
                    trace_id, index, category,
                )
                continue

            linked_fr_id = item.get("linked_fr_id")
            if linked_fr_id is not None and linked_fr_id not in valid_fr_ids:
                logger.debug(
                    "trace_id=%s | non_functional_model.py | NFR at index=%d references unknown fr_id='%s', treating as global",
                    trace_id, index, linked_fr_id,
                )
                linked_fr_id = None

            threshold_value = item.get("threshold_value")
            threshold_value = float(threshold_value) if threshold_value is not None else None

            nfr: ExtractedNFR = {
                "category": category,
                "constraint": str(item["constraint"]),
                "linked_fr_id": linked_fr_id,
                "threshold_value": threshold_value,
                "threshold_unit": item.get("threshold_unit"),
            }
            results.append(nfr)
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(
                "trace_id=%s | non_functional_model.py | skipping malformed NFR item at index=%d | error=%s",
                trace_id, index, str(exc),
            )
            continue

    if not results:
        logger.warning("trace_id=%s | non_functional_model.py | LLM returned zero usable NFRs", trace_id)
        return None

    logger.info(
        "trace_id=%s | non_functional_model.py | LLM generated %d NFRs successfully",
        trace_id, len(results),
    )
    return results