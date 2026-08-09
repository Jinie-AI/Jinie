"""
requirement.py

Stage 1 of the SRS pipeline. Takes the user's raw requirement prompt
(English, Urdu, or Roman Urdu) and returns a RawRequirementFeatures
object: normalized text, detected language, extracted keywords,
candidate entities, and coarse intent tags.

ML NOTE:
Real semantic extraction is performed by an LLM (Groq's free API),
called through models/requirement_model.py -> models/llm_client.py.
The regex/keyword-matching logic below is kept ONLY as a fallback
path — it runs automatically if the LLM call fails (missing key,
network error, malformed response), so the pipeline never crashes
just because the model call didn't go through. See `_run_ml_extraction`.
"""

from __future__ import annotations

import logging
import re
import time
from typing import List, Tuple

from .requirement_model import extract_with_llm
from common.schemas import RawRequirementFeatures, SupportedLanguage
from logger import Logger

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Lightweight language heuristics (placeholder for a real langid model)
# ---------------------------------------------------------------------

_URDU_UNICODE_RANGE = re.compile(r"[\u0600-\u06FF]")
_ROMAN_URDU_MARKERS = {
    "hai", "kya", "chahiye", "banao", "app", "wala", "krna", "krein",
    "mein", "aur", "nahi", "hoga", "bnado", "screen", "banana",
}

_INTENT_KEYWORD_MAP = {
    "auth": ["login", "signup", "signin", "register", "password", "otp", "authentication"],
    "social_feed": ["feed", "post", "like", "comment", "share", "timeline", "story"],
    "ecommerce": ["cart", "checkout", "product", "price", "order", "payment", "buy"],
    "messaging": ["chat", "message", "inbox", "notification", "call"],
    "profile": ["profile", "avatar", "bio", "settings", "account"],
    "dashboard": ["dashboard", "analytics", "chart", "stats", "report"],
}

_STOPWORDS = {
    "the", "a", "an", "to", "and", "of", "for", "in", "on", "with",
    "app", "should", "want", "please", "make", "create", "build",
}


def _detect_language(text: str) -> SupportedLanguage:
    if _URDU_UNICODE_RANGE.search(text):
        return SupportedLanguage.URDU
    lowered = text.lower()
    roman_hits = sum(1 for marker in _ROMAN_URDU_MARKERS if marker in lowered)
    if roman_hits >= 2:
        return SupportedLanguage.ROMAN_URDU
    if text.strip():
        return SupportedLanguage.ENGLISH
    return SupportedLanguage.UNKNOWN


def _normalize_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return normalized


def _extract_keywords(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z\u0600-\u06FF]+", text.lower())
    keywords = [t for t in tokens if t not in _STOPWORDS and len(t) > 2]
    # de-duplicate while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    return unique_keywords


def _extract_intent_tags(keywords: List[str]) -> List[str]:
    tags = []
    keyword_set = set(keywords)
    for intent, markers in _INTENT_KEYWORD_MAP.items():
        if keyword_set.intersection(markers):
            tags.append(intent)
    return tags


def _extract_candidate_entities(keywords: List[str]) -> List[str]:
    # Rule-based fallback: nouns that commonly map to persistable objects.
    noun_like = {
        "user", "product", "order", "post", "comment", "message",
        "profile", "cart", "payment", "notification", "review",
    }
    return [kw for kw in keywords if kw in noun_like]


# ---------------------------------------------------------------------
# MODEL PLACEHOLDER
# ---------------------------------------------------------------------
def _run_ml_extraction(normalized_text: str, trace_id: str) -> Tuple[List[str], List[str], List[str], float]:
    """
    Calls the LLM (Groq free tier, via models/requirement_model.py) to
    perform real semantic extraction of keywords, intent tags, and
    candidate entities from `normalized_text`. If the call fails for
    any reason (missing API key, network error, malformed response),
    this function falls back to the deterministic regex/keyword-
    matching heuristic below rather than crashing the pipeline.
    """
    llm_result = extract_with_llm(normalized_text, trace_id)

    if llm_result is not None:
        logger.info(
            "trace_id=%s | requirement.py | using LLM-extracted features (model path)",
            trace_id,
        )
        return (
            llm_result["keywords"],
            llm_result["intent_tags"],
            llm_result["candidate_entities"],
            llm_result["confidence_score"],
        )

    logger.warning(
        "trace_id=%s | requirement.py | LLM extraction unavailable, falling back to heuristic path",
        trace_id,
    )
    keywords = _extract_keywords(normalized_text)
    intents = _extract_intent_tags(keywords)
    entities = _extract_candidate_entities(keywords)
    confidence = 0.55 if keywords else 0.1  # heuristic fallback confidence is intentionally modest
    return keywords, intents, entities, confidence


def extract_raw_features(prompt: str, trace_id: str) -> RawRequirementFeatures:
    """
    Entry point for Stage 1. Takes the raw user prompt and trace_id and
    returns a fully populated RawRequirementFeatures object.
    """
    start_time = time.perf_counter()
    logger_instance = Logger(trace_id=trace_id)
    logger_instance.log_event("requirement.py", f"Starting requirement extraction | prompt_length={len(prompt)}")
    logger.info("trace_id=%s | requirement.py | stage=start | prompt_length=%d", trace_id, len(prompt))

    try:
        if not prompt or not prompt.strip():
            logger_instance.log_event("requirement.py", "Empty prompt received, returning empty feature set", level="WARNING")
            logger.warning("trace_id=%s | requirement.py | empty prompt received, returning empty feature set", trace_id)
            return RawRequirementFeatures(
                trace_id=trace_id,
                original_prompt=prompt or "",
                detected_language=SupportedLanguage.UNKNOWN,
                normalized_text="",
                extracted_keywords=[],
                intent_tags=[],
                candidate_entities=[],
                confidence_score=0.0,
            )

        language = _detect_language(prompt)
        normalized = _normalize_text(prompt)
        logger.debug("trace_id=%s | requirement.py | detected_language=%s", trace_id, language.value)

        keywords, intents, entities, confidence = _run_ml_extraction(normalized, trace_id)

        result = RawRequirementFeatures(
            trace_id=trace_id,
            original_prompt=prompt,
            detected_language=language,
            normalized_text=normalized,
            extracted_keywords=keywords,
            intent_tags=intents,
            candidate_entities=entities,
            confidence_score=confidence,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger_instance.log_event(
            "requirement.py",
            f"Stage complete | keywords={len(keywords)} intents={len(intents)} entities={len(entities)} duration_ms={elapsed_ms:.2f}",
        )
        logger.info(
            "trace_id=%s | requirement.py | stage=complete | keywords=%d intents=%d entities=%d duration_ms=%.2f",
            trace_id, len(keywords), len(intents), len(entities), elapsed_ms,
        )
        return result

    except Exception as exc:  # noqa: BLE001
        logger_instance.log_event("requirement.py", f"Stage failed | error={str(exc)}", level="CRITICAL")
        logger.critical(
            "trace_id=%s | requirement.py | stage=failed | error=%s", trace_id, str(exc), exc_info=True
        )
        # Fallback: return a minimally valid object rather than crashing the pipeline
        return RawRequirementFeatures(
            trace_id=trace_id,
            original_prompt=prompt or "",
            detected_language=SupportedLanguage.UNKNOWN,
            normalized_text=prompt or "",
            extracted_keywords=[],
            intent_tags=[],
            candidate_entities=[],
            confidence_score=0.0,
        )