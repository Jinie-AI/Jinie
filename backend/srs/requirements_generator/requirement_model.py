"""
requirement_model.py

Domain-specific layer on top of llm_client.py. Knows nothing about
HTTP — it only knows: what prompt to send the LLM for requirement
extraction, and how to parse the model's JSON reply into the plain
dict shape that requirement.py expects.

Uses Groq's free API (llama-3.3-70b-versatile by default) via
llm_client.py. This is the file you'd edit if you ever change *what*
you ask the model to extract (e.g. add sentiment, add urgency scoring)
without touching the HTTP/auth plumbing in llm_client.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()  # single shared client instance for this module


class ExtractedFeatures(TypedDict):
    detected_language: str          # "english" | "urdu" | "roman_urdu" | "unknown"
    keywords: List[str]
    intent_tags: List[str]
    candidate_entities: List[str]
    confidence_score: float


_SYSTEM_PROMPT = """You are a requirement-extraction engine for a mobile app \
generation pipeline. Given a user's raw app description (which may be in \
English, Urdu script, or Roman Urdu), extract structured features.

Respond with ONLY a single valid JSON object, no markdown fences, no \
preamble, no explanation. The JSON must have exactly these keys:

{
  "detected_language": "english" | "urdu" | "roman_urdu" | "unknown",
  "keywords": [list of lowercase single-word or short-phrase keywords, \
max 15],
  "intent_tags": [short, domain-neutral capability labels inferred from the request, \
such as "authentication", "scheduling", "inventory", "learning", or "reporting"],
  "candidate_entities": [list of lowercase singular nouns that represent \
persistable data objects the app would need to store],
  "confidence_score": float between 0.0 and 1.0 representing how clear \
and unambiguous the extraction was
}

Do not invent features not implied by the text. If the text is too \
vague to extract something, return an empty list for that key rather \
than guessing."""


def _build_user_prompt(normalized_text: str) -> str:
    return f"App description:\n\"\"\"\n{normalized_text}\n\"\"\""


# Backwards-compatible alias (existing tests import this private name directly)
_strip_markdown_fences = strip_markdown_fences


def extract_with_llm(normalized_text: str, trace_id: str) -> Optional[ExtractedFeatures]:
    """
    Calls the LLM (Groq, free tier) to extract structured requirement
    features from `normalized_text`. Returns None (never raises) if
    the call fails or the response can't be parsed — the caller
    (requirement.py) is responsible for falling back to the heuristic
    path in that case.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(normalized_text)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.1)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | requirement_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = _strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning(
            "trace_id=%s | requirement_model.py | LLM response was not valid JSON | error=%s | raw=%s",
            trace_id, str(exc), cleaned[:300],
        )
        return None

    try:
        result: ExtractedFeatures = {
            "detected_language": str(parsed.get("detected_language", "unknown")).lower(),
            "keywords": [str(k).lower() for k in parsed.get("keywords", []) if isinstance(k, (str, int, float))],
            "intent_tags": [str(t).lower() for t in parsed.get("intent_tags", [])],
            "candidate_entities": [str(e).lower() for e in parsed.get("candidate_entities", [])],
            "confidence_score": float(parsed.get("confidence_score", 0.5)),
        }
        logger.info(
            "trace_id=%s | requirement_model.py | LLM extraction succeeded | keywords=%d intents=%d entities=%d confidence=%.2f",
            trace_id, len(result["keywords"]), len(result["intent_tags"]), len(result["candidate_entities"]), result["confidence_score"],
        )
        return result
    except (TypeError, ValueError) as exc:
        logger.warning(
            "trace_id=%s | requirement_model.py | LLM JSON had wrong shape/types | error=%s",
            trace_id, str(exc),
        )
        return None
