"""
stack_identifier_model.py

Domain-specific LLM layer for Stage 7 (Tech Stack Identification).
Given the FR/NFR/entity summaries, asks the LLM to pick concrete
framework/library targets with reasoning, instead of relying only on
the fixed if/else rules in stack_identifier.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from common.llm_client import LLMClient, LLMAPIError
from common.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()


class ExtractedStack(TypedDict):
    state_management: str
    ui_library: str
    backend_service: str
    reasoning: List[str]


_SYSTEM_PROMPT = """You are a mobile tech stack selection engine for a \
React Native (Expo) app generation pipeline. Given a summary of \
Functional Requirements, Non-Functional Requirements, and entity count, \
recommend concrete library choices.

Respond with ONLY a single valid JSON object, no markdown fences, no \
preamble, no explanation, with exactly these keys:

{
  "state_management": "e.g. 'Zustand', 'React Context + useReducer', \
'Redux Toolkit'",
  "ui_library": "e.g. 'Tamagui', 'Tamagui + Victory Native', \
'NativeBase'",
  "backend_service": "e.g. 'Firebase Firestore', 'Firebase Firestore + \
Cloud Functions + Stripe', 'Supabase'",
  "reasoning": [list of short sentences, one per major decision, \
explaining WHY each choice fits this specific app]
}

The framework is always React Native (Expo) and navigation is always \
React Navigation — do not include those in your response, only the \
three keys above. Base your reasoning on the actual FR/NFR content \
given, not generic advice."""


def _build_user_prompt(fr_summaries: List[dict], nfr_summaries: List[dict], entity_count: int) -> str:
    fr_lines = "\n".join(f"- {fr['fr_id']}: {fr['description']} ({fr['priority']})" for fr in fr_summaries)
    nfr_lines = "\n".join(f"- {nfr['category']}: {nfr['constraint']}" for nfr in nfr_summaries) or "(none)"
    return (
        f"Functional Requirements:\n{fr_lines}\n\n"
        f"Non-Functional Requirements:\n{nfr_lines}\n\n"
        f"Total distinct data entities: {entity_count}"
    )


def identify_stack_with_llm(
    fr_summaries: List[dict], nfr_summaries: List[dict], entity_count: int, trace_id: str
) -> Optional[ExtractedStack]:
    """
    Calls the LLM to select state management, UI library, and backend
    service with reasoning. Returns None (never raises) on any failure
    — caller falls back to the fixed if/else rules in stack_identifier.py.
    """
    if not fr_summaries:
        logger.debug("trace_id=%s | stack_identifier_model.py | no FRs provided, skipping LLM call", trace_id)
        return None

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(fr_summaries, nfr_summaries, entity_count)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.3, max_tokens=800)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | stack_identifier_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ValueError("Expected a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "trace_id=%s | stack_identifier_model.py | LLM response was not valid JSON | error=%s | raw=%s",
            trace_id, str(exc), cleaned[:300],
        )
        return None

    try:
        result: ExtractedStack = {
            "state_management": str(parsed["state_management"]),
            "ui_library": str(parsed["ui_library"]),
            "backend_service": str(parsed["backend_service"]),
            "reasoning": [str(r) for r in parsed.get("reasoning", [])],
        }
    except KeyError as exc:
        logger.warning(
            "trace_id=%s | stack_identifier_model.py | LLM JSON missing required key | error=%s",
            trace_id, str(exc),
        )
        return None

    logger.info(
        "trace_id=%s | stack_identifier_model.py | LLM selected stack successfully",
        trace_id,
    )
    return result