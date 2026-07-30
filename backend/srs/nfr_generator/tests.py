"""
tests.py — nfr_generator

Covers: non_functional.py (Stage 3 entry point + rule-based fallback)
and non_functional_model.py (LLM prompt/parsing layer). All network
calls are mocked — no real Groq API key or internet connection needed.

Run with:
    cd backend/srs/nfr_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import (
    FunctionalRequirement,
    FunctionalRequirementSet,
    Priority,
    NFRCategory,
)
from common.llm_client import LLMAPIError
from nfr_generator.non_functional import generate_non_functional_requirements
from nfr_generator.non_functional_model import generate_nfrs_with_llm


def _make_fr_set() -> FunctionalRequirementSet:
    fr = FunctionalRequirement(
        fr_id="FR-001",
        description="User logs in with email and password.",
        actors=["RegisteredUser"],
        inputs=["email", "password"],
        outputs=["auth_token"],
        priority=Priority.CRITICAL,
        source_keywords=["login", "password"],
    )
    return FunctionalRequirementSet(trace_id="test-trace", requirements=[fr])


# =====================================================================
# non_functional_model.py — LLM layer
# =====================================================================

VALID_NFR_JSON = """[
  {
    "category": "security",
    "constraint": "Password must be transmitted over TLS only.",
    "linked_fr_id": "FR-001",
    "threshold_value": null,
    "threshold_unit": null
  },
  {
    "category": "performance",
    "constraint": "Login must complete within 300ms.",
    "linked_fr_id": "FR-001",
    "threshold_value": 300,
    "threshold_unit": "ms"
  }
]"""


@patch("nfr_generator.non_functional_model._client.chat_completion")
def test_valid_nfr_list_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_NFR_JSON
    fr_summaries = [{"fr_id": "FR-001", "description": "User logs in.", "priority": "critical"}]
    result = generate_nfrs_with_llm(fr_summaries, trace_id="t1")
    assert result is not None
    assert len(result) == 2
    assert result[0]["category"] == "security"
    assert result[1]["threshold_value"] == pytest.approx(300.0)


@patch("nfr_generator.non_functional_model._client.chat_completion")
def test_markdown_fenced_response_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_NFR_JSON}\n```"
    fr_summaries = [{"fr_id": "FR-001", "description": "User logs in.", "priority": "critical"}]
    result = generate_nfrs_with_llm(fr_summaries, trace_id="t2")
    assert result is not None
    assert len(result) == 2


@patch("nfr_generator.non_functional_model._client.chat_completion")
def test_llm_api_error_returns_none(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = generate_nfrs_with_llm(fr_summaries, trace_id="t3")
    assert result is None


def test_empty_fr_summaries_skips_llm_call_returns_none():
    result = generate_nfrs_with_llm([], trace_id="t4")
    assert result is None


@patch("nfr_generator.non_functional_model._client.chat_completion")
def test_invalid_category_is_skipped(mock_chat):
    mock_chat.return_value = """[
      {"category": "not_a_real_category", "constraint": "x", "linked_fr_id": null, "threshold_value": null, "threshold_unit": null},
      {"category": "security", "constraint": "Valid one.", "linked_fr_id": "FR-001", "threshold_value": null, "threshold_unit": null}
    ]"""
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = generate_nfrs_with_llm(fr_summaries, trace_id="t5")
    assert result is not None
    assert len(result) == 1
    assert result[0]["category"] == "security"


@patch("nfr_generator.non_functional_model._client.chat_completion")
def test_unknown_fr_id_reference_becomes_global(mock_chat):
    mock_chat.return_value = """[
      {"category": "security", "constraint": "x", "linked_fr_id": "FR-999", "threshold_value": null, "threshold_unit": null}
    ]"""
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = generate_nfrs_with_llm(fr_summaries, trace_id="t6")
    assert result is not None
    assert result[0]["linked_fr_id"] is None  # unknown FR-999 downgraded to global


@patch("nfr_generator.non_functional_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "not json"
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = generate_nfrs_with_llm(fr_summaries, trace_id="t7")
    assert result is None


# =====================================================================
# non_functional.py — Stage 3 entry point
# =====================================================================

@patch("nfr_generator.non_functional.generate_nfrs_with_llm")
def test_uses_llm_result_when_available(mock_generate):
    mock_generate.return_value = [
        {
            "category": "security",
            "constraint": "Use TLS.",
            "linked_fr_id": "FR-001",
            "threshold_value": None,
            "threshold_unit": None,
        }
    ]
    fr_set = _make_fr_set()
    result = generate_non_functional_requirements(fr_set, trace_id="t8")
    assert len(result.requirements) == 1
    assert result.requirements[0].category == NFRCategory.SECURITY
    assert result.requirements[0].linked_fr_id == "FR-001"


@patch("nfr_generator.non_functional.generate_nfrs_with_llm")
def test_falls_back_to_rules_when_llm_unavailable(mock_generate):
    mock_generate.return_value = None
    fr_set = _make_fr_set()
    result = generate_non_functional_requirements(fr_set, trace_id="t9")
    assert len(result.requirements) > 0  # baseline + password-triggered constraint apply


@patch("nfr_generator.non_functional.generate_nfrs_with_llm")
def test_rule_fallback_links_back_to_correct_fr_id(mock_generate):
    mock_generate.return_value = None
    fr_set = _make_fr_set()
    result = generate_non_functional_requirements(fr_set, trace_id="t10")
    assert all(nfr.linked_fr_id == "FR-001" for nfr in result.requirements)


@patch("nfr_generator.non_functional.generate_nfrs_with_llm")
def test_trace_id_propagated(mock_generate):
    mock_generate.return_value = None
    fr_set = _make_fr_set()
    result = generate_non_functional_requirements(fr_set, trace_id="trace-nfr-777")
    assert result.trace_id == "trace-nfr-777"