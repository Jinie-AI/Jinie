"""
test_all_requirement_pipeline.py

Single consolidated test file covering the entire Stage 1 (requirement
extraction) chain:
    - models/llm_client.py       (LLMClient / LLMAPIError)
    - models/requirement_model.py (extract_with_llm, JSON parsing)
    - requirement.py              (extract_raw_features, heuristic fallback helpers)

All network calls are mocked — no real Groq API key or internet
connection needed to run this file.

Run with:
    cd backend/srs
    python -m pytest test_all_requirement_pipeline.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from models.llm_client import LLMClient, LLMAPIError
from models.requirement_model import extract_with_llm, _strip_markdown_fences

# from requirements import (
#     extract_raw_features,
#     _detect_language,
#     _extract_keywords,
#     _extract_intent_tags,
# )


# =====================================================================
# SECTION 1 — models/llm_client.py
# =====================================================================

@pytest.fixture
def client():
    return LLMClient(api_key="gsk_fake_test_key", model="llama-3.3-70b-versatile")


def _fake_response(content: str, status_code: int = 200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.raise_for_status = MagicMock()
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_resp)
    mock_resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    return mock_resp


def test_missing_api_key_raises_immediately():
    client_without_key = LLMClient(api_key=None)
    with pytest.raises(LLMAPIError):
        client_without_key.chat_completion(messages=[{"role": "user", "content": "hi"}], trace_id="t1")


@patch("models.llm_client.requests.post")
def test_successful_call_returns_content(mock_post, client):
    mock_post.return_value = _fake_response('{"keywords": ["login"]}')
    result = client.chat_completion(messages=[{"role": "user", "content": "hi"}], trace_id="t2")
    assert result == '{"keywords": ["login"]}'
    mock_post.assert_called_once()


@patch("models.llm_client.requests.post")
def test_auth_error_does_not_retry(mock_post, client):
    mock_post.return_value = _fake_response("", status_code=401)
    with pytest.raises(LLMAPIError):
        client.chat_completion(messages=[{"role": "user", "content": "hi"}], trace_id="t3")
    assert mock_post.call_count == 1


@patch("models.llm_client.requests.post")
def test_network_error_retries_then_raises(mock_post, client):
    mock_post.side_effect = requests.exceptions.ConnectionError("network down")
    with pytest.raises(LLMAPIError):
        client.chat_completion(messages=[{"role": "user", "content": "hi"}], trace_id="t4")
    assert mock_post.call_count == 3


@patch("models.llm_client.requests.post")
def test_rate_limit_status_retries(mock_post, client):
    mock_post.return_value = _fake_response("", status_code=429)
    with pytest.raises(LLMAPIError):
        client.chat_completion(messages=[{"role": "user", "content": "hi"}], trace_id="t5")
    assert mock_post.call_count == 3


@patch("models.llm_client.requests.post")
def test_malformed_response_raises_after_retries(mock_post, client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"unexpected": "shape"}
    mock_post.return_value = mock_resp
    with pytest.raises(LLMAPIError):
        client.chat_completion(messages=[{"role": "user", "content": "hi"}], trace_id="t6")


# =====================================================================
# SECTION 2 — models/requirement_model.py
# =====================================================================

VALID_JSON_RESPONSE = """{
  "detected_language": "english",
  "keywords": ["login", "post", "comment"],
  "intent_tags": ["auth", "social_feed"],
  "candidate_entities": ["user", "post", "comment"],
  "confidence_score": 0.92
}"""


@patch("models.requirement_model._client.chat_completion")
def test_valid_response_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_JSON_RESPONSE
    result = extract_with_llm("I want an app where users can log in and post updates", trace_id="t7")
    assert result is not None
    assert result["detected_language"] == "english"
    assert "login" in result["keywords"]
    assert "auth" in result["intent_tags"]
    assert "user" in result["candidate_entities"]
    assert result["confidence_score"] == pytest.approx(0.92)


@patch("models.requirement_model._client.chat_completion")
def test_response_wrapped_in_markdown_fences_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_JSON_RESPONSE}\n```"
    result = extract_with_llm("some prompt", trace_id="t8")
    assert result is not None
    assert result["detected_language"] == "english"


@patch("models.requirement_model._client.chat_completion")
def test_llm_api_error_returns_none_not_raise(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    result = extract_with_llm("some prompt", trace_id="t9")
    assert result is None


@patch("models.requirement_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "this is not json at all"
    result = extract_with_llm("some prompt", trace_id="t10")
    assert result is None


@patch("models.requirement_model._client.chat_completion")
def test_missing_keys_get_safe_defaults(mock_chat):
    mock_chat.return_value = '{"detected_language": "urdu"}'
    result = extract_with_llm("some prompt", trace_id="t11")
    assert result is not None
    assert result["detected_language"] == "urdu"
    assert result["keywords"] == []
    assert result["intent_tags"] == []
    assert result["candidate_entities"] == []
    assert result["confidence_score"] == pytest.approx(0.5)


@patch("models.requirement_model._client.chat_completion")
def test_wrong_types_in_json_returns_none(mock_chat):
    mock_chat.return_value = '{"confidence_score": "not_a_number"}'
    result = extract_with_llm("some prompt", trace_id="t12")
    assert result is None


def test_strip_markdown_fences_removes_both_ends():
    raw = "```json\n{\"a\": 1}\n```"
    assert _strip_markdown_fences(raw) == '{"a": 1}'


def test_strip_markdown_fences_noop_on_plain_json():
    raw = '{"a": 1}'
    assert _strip_markdown_fences(raw) == raw


# =====================================================================
# SECTION 3 — requirement.py
# =====================================================================

@patch("requirement.extract_with_llm")
def test_uses_llm_result_when_available(mock_extract):
    mock_extract.return_value = {
        "detected_language": "english",
        "keywords": ["login", "post"],
        "intent_tags": ["auth", "social_feed"],
        "candidate_entities": ["user", "post"],
        "confidence_score": 0.9,
    }
    result = extract_raw_features("Build an app with login and posting", trace_id="t13")
    assert result.confidence_score == pytest.approx(0.9)
    assert "auth" in result.intent_tags
    assert "user" in result.candidate_entities


@patch("requirement.extract_with_llm")
def test_falls_back_to_heuristic_when_llm_unavailable(mock_extract):
    mock_extract.return_value = None
    result = extract_raw_features("I want an app for login and posting", trace_id="t14")
    assert result is not None
    assert result.confidence_score <= 0.55
    assert isinstance(result.extracted_keywords, list)


@patch("requirement.extract_with_llm")
def test_empty_prompt_returns_empty_features_without_calling_llm(mock_extract):
    result = extract_raw_features("   ", trace_id="t15")
    assert result.normalized_text == ""
    assert result.extracted_keywords == []
    assert result.confidence_score == 0.0
    mock_extract.assert_not_called()


@patch("requirement.extract_with_llm")
def test_trace_id_is_propagated_into_output(mock_extract):
    mock_extract.return_value = None
    result = extract_raw_features("Build a chat app", trace_id="trace-xyz-123")
    assert result.trace_id == "trace-xyz-123"


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
    assert "posting" in keywords
    assert "the" not in keywords
    assert "want" not in keywords


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