"""
tests.py — requirements_generator

Covers: requirement.py (Stage 1 entry point + heuristic helpers) and
requirement_model.py (LLM prompt/parsing layer). All network calls are
mocked — no real Groq API key or internet connection needed.

Run with:
    cd backend/srs/requirements_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import SupportedLanguage
from requirements_generator.requirement import (
    extract_raw_features,
    _detect_language,
    _extract_keywords,
    _extract_intent_tags,
)
from requirements_generator.requirement_model import extract_with_llm
from common.llm_client import LLMAPIError


# =====================================================================
# requirement_model.py — LLM layer
# =====================================================================

VALID_JSON_RESPONSE = """{
  "detected_language": "english",
  "keywords": ["login", "post", "comment"],
  "intent_tags": ["auth", "social_feed"],
  "candidate_entities": ["user", "post", "comment"],
  "confidence_score": 0.92
}"""


@patch("requirements_generator.requirement_model._client.chat_completion")
def test_valid_response_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_JSON_RESPONSE
    result = extract_with_llm("I want an app where users can log in and post updates", trace_id="t1")
    assert result is not None
    assert result["detected_language"] == "english"
    assert "login" in result["keywords"]
    assert "auth" in result["intent_tags"]
    assert result["confidence_score"] == pytest.approx(0.92)


@patch("requirements_generator.requirement_model._client.chat_completion")
def test_response_wrapped_in_markdown_fences_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_JSON_RESPONSE}\n```"
    result = extract_with_llm("some prompt", trace_id="t2")
    assert result is not None
    assert result["detected_language"] == "english"


@patch("requirements_generator.requirement_model._client.chat_completion")
def test_llm_api_error_returns_none_not_raise(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    result = extract_with_llm("some prompt", trace_id="t3")
    assert result is None


@patch("requirements_generator.requirement_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "this is not json at all"
    result = extract_with_llm("some prompt", trace_id="t4")
    assert result is None


@patch("requirements_generator.requirement_model._client.chat_completion")
def test_missing_keys_get_safe_defaults(mock_chat):
    mock_chat.return_value = '{"detected_language": "urdu"}'
    result = extract_with_llm("some prompt", trace_id="t5")
    assert result is not None
    assert result["detected_language"] == "urdu"
    assert result["keywords"] == []
    assert result["confidence_score"] == pytest.approx(0.5)


@patch("requirements_generator.requirement_model._client.chat_completion")
def test_wrong_types_in_json_returns_none(mock_chat):
    mock_chat.return_value = '{"confidence_score": "not_a_number"}'
    result = extract_with_llm("some prompt", trace_id="t6")
    assert result is None


# =====================================================================
# requirement.py — Stage 1 entry point
# =====================================================================

@patch("requirements_generator.requirement.extract_with_llm")
def test_uses_llm_result_when_available(mock_extract):
    mock_extract.return_value = {
        "detected_language": "english",
        "keywords": ["login", "post"],
        "intent_tags": ["auth", "social_feed"],
        "candidate_entities": ["user", "post"],
        "confidence_score": 0.9,
    }
    result = extract_raw_features("Build an app with login and posting", trace_id="t7")
    assert result.confidence_score == pytest.approx(0.9)
    assert "auth" in result.intent_tags


@patch("requirements_generator.requirement.extract_with_llm")
def test_falls_back_to_heuristic_when_llm_unavailable(mock_extract):
    mock_extract.return_value = None
    result = extract_raw_features("I want an app for login and posting", trace_id="t8")
    assert result is not None
    assert result.confidence_score <= 0.55
    assert isinstance(result.extracted_keywords, list)


@patch("requirements_generator.requirement.extract_with_llm")
def test_empty_prompt_returns_empty_features_without_calling_llm(mock_extract):
    result = extract_raw_features("   ", trace_id="t9")
    assert result.normalized_text == ""
    assert result.extracted_keywords == []
    assert result.confidence_score == 0.0
    mock_extract.assert_not_called()


@patch("requirements_generator.requirement.extract_with_llm")
def test_trace_id_is_propagated_into_output(mock_extract):
    mock_extract.return_value = None
    result = extract_raw_features("Build a chat app", trace_id="trace-xyz-123")
    assert result.trace_id == "trace-xyz-123"


# =====================================================================
# Heuristic helper functions (fallback path only)
# =====================================================================

def test_detect_language_english():
    assert _detect_language("I want to build a social app") == SupportedLanguage.ENGLISH


def test_detect_language_urdu_script():
    assert _detect_language("مجھے ایک ایپ چاہیے") == SupportedLanguage.URDU


def test_detect_language_roman_urdu():
    assert _detect_language("mujhe aik app banani hai jo login kare aur post kare") == SupportedLanguage.ROMAN_URDU


def test_detect_language_empty_string():
    assert _detect_language("") == SupportedLanguage.UNKNOWN


def test_extract_keywords_filters_stopwords():
    keywords = _extract_keywords("I want to create an app for login and posting")
    assert "login" in keywords
    assert "the" not in keywords


def test_extract_keywords_deduplicates():
    keywords = _extract_keywords("login login login post")
    assert keywords.count("login") == 1


def test_extract_intent_tags_matches_known_markers():
    tags = _extract_intent_tags(["login", "password", "feed", "checkout"])
    assert "auth" in tags
    assert "social_feed" in tags
    assert "ecommerce" in tags


def test_extract_intent_tags_empty_when_no_match():
    tags = _extract_intent_tags(["banana", "sunshine"])
    assert tags == []