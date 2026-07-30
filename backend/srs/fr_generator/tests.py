"""
tests.py — fr_generator

Covers: functional.py (Stage 2 entry point + template fallback) and
functional_model.py (LLM prompt/parsing layer). All network calls are
mocked — no real Groq API key or internet connection needed.

Run with:
    cd backend/srs/fr_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import RawRequirementFeatures, SupportedLanguage, Priority
from common.llm_client import LLMAPIError
from fr_generator.functional import generate_functional_requirements
from fr_generator.functional_model import generate_frs_with_llm


def _make_raw_features(**overrides) -> RawRequirementFeatures:
    defaults = dict(
        trace_id="test-trace",
        original_prompt="an app for login and posting",
        detected_language=SupportedLanguage.ENGLISH,
        normalized_text="an app for login and posting",
        extracted_keywords=["login", "post"],
        intent_tags=["auth"],
        candidate_entities=["user"],
        confidence_score=0.8,
    )
    defaults.update(overrides)
    return RawRequirementFeatures(**defaults)


# =====================================================================
# functional_model.py — LLM layer
# =====================================================================

VALID_FR_JSON = """[
  {
    "description": "User logs in with email and password.",
    "actors": ["RegisteredUser"],
    "inputs": ["email", "password"],
    "outputs": ["auth_token"],
    "priority": "critical"
  },
  {
    "description": "User creates a new post.",
    "actors": ["AuthenticatedUser"],
    "inputs": ["post_text"],
    "outputs": ["created_post_object"],
    "priority": "high"
  }
]"""


@patch("fr_generator.functional_model._client.chat_completion")
def test_valid_fr_list_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_FR_JSON
    result = generate_frs_with_llm("an app for login and posting", ["login", "post"], ["auth"], trace_id="t1")
    assert result is not None
    assert len(result) == 2
    assert result[0]["priority"] == "critical"
    assert "email" in result[0]["inputs"]


@patch("fr_generator.functional_model._client.chat_completion")
def test_markdown_fenced_response_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_FR_JSON}\n```"
    result = generate_frs_with_llm("some prompt", [], [], trace_id="t2")
    assert result is not None
    assert len(result) == 2


@patch("fr_generator.functional_model._client.chat_completion")
def test_llm_api_error_returns_none(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    result = generate_frs_with_llm("some prompt", [], [], trace_id="t3")
    assert result is None


@patch("fr_generator.functional_model._client.chat_completion")
def test_non_array_response_returns_none(mock_chat):
    mock_chat.return_value = '{"not": "an array"}'
    result = generate_frs_with_llm("some prompt", [], [], trace_id="t4")
    assert result is None


@patch("fr_generator.functional_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "not json"
    result = generate_frs_with_llm("some prompt", [], [], trace_id="t5")
    assert result is None


@patch("fr_generator.functional_model._client.chat_completion")
def test_malformed_item_in_array_is_skipped_not_fatal(mock_chat):
    mixed = """[
      {"description": "Valid FR", "actors": ["User"], "inputs": [], "outputs": [], "priority": "medium"},
      {"missing_description_key": true}
    ]"""
    mock_chat.return_value = mixed
    result = generate_frs_with_llm("some prompt", [], [], trace_id="t6")
    assert result is not None
    assert len(result) == 1  # malformed item skipped, valid one kept


@patch("fr_generator.functional_model._client.chat_completion")
def test_empty_array_returns_none(mock_chat):
    mock_chat.return_value = "[]"
    result = generate_frs_with_llm("some prompt", [], [], trace_id="t7")
    assert result is None


# =====================================================================
# functional.py — Stage 2 entry point
# =====================================================================

@patch("fr_generator.functional.generate_frs_with_llm")
def test_uses_llm_result_when_available(mock_generate):
    mock_generate.return_value = [
        {
            "description": "User logs in.",
            "actors": ["RegisteredUser"],
            "inputs": ["email", "password"],
            "outputs": ["auth_token"],
            "priority": "critical",
        }
    ]
    raw = _make_raw_features()
    result = generate_functional_requirements(raw, trace_id="t8")
    assert len(result.requirements) == 1
    assert result.requirements[0].fr_id == "FR-001"
    assert result.requirements[0].priority == Priority.CRITICAL


@patch("fr_generator.functional.generate_frs_with_llm")
def test_falls_back_to_templates_when_llm_unavailable(mock_generate):
    mock_generate.return_value = None
    raw = _make_raw_features(intent_tags=["auth"])
    result = generate_functional_requirements(raw, trace_id="t9")
    assert len(result.requirements) > 0  # template archetype for "auth" kicks in


@patch("fr_generator.functional.generate_frs_with_llm")
def test_unknown_intent_falls_back_to_default_template(mock_generate):
    mock_generate.return_value = None
    raw = _make_raw_features(intent_tags=["totally_unknown_intent"])
    result = generate_functional_requirements(raw, trace_id="t10")
    assert len(result.requirements) >= 1  # default fallback template used


@patch("fr_generator.functional.generate_frs_with_llm")
def test_invalid_priority_from_llm_defaults_to_medium(mock_generate):
    mock_generate.return_value = [
        {
            "description": "Some action.",
            "actors": ["User"],
            "inputs": [],
            "outputs": [],
            "priority": "not_a_real_priority",
        }
    ]
    raw = _make_raw_features()
    result = generate_functional_requirements(raw, trace_id="t11")
    assert result.requirements[0].priority == Priority.MEDIUM


@patch("fr_generator.functional.generate_frs_with_llm")
def test_trace_id_propagated(mock_generate):
    mock_generate.return_value = None
    raw = _make_raw_features(intent_tags=["auth"])
    result = generate_functional_requirements(raw, trace_id="trace-abc-999")
    assert result.trace_id == "trace-abc-999"