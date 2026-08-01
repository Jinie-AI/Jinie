"""
tests.py — stack_identifier_generator

Covers: stack_identifier.py (Stage 7 entry point, LLM path + rule
fallback) and stack_identifier_model.py (LLM prompt/parsing layer).
LLM calls are mocked — no real Groq API key or internet connection
needed.

Run with:
    cd backend/srs/stack_identifier_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import (
    FunctionalRequirement,
    FunctionalRequirementSet,
    NonFunctionalRequirement,
    NonFunctionalRequirementSet,
    Entity,
    EntitySet,
    Priority,
    NFRCategory,
)
from common.llm_client import LLMAPIError
from stack_identifier_generator.stack_identifier import identify_tech_stack
from stack_identifier_generator.stack_identifier_model import identify_stack_with_llm


def _fr(fr_id, description):
    return FunctionalRequirement(
        fr_id=fr_id, description=description, actors=["User"],
        inputs=[], outputs=[], priority=Priority.MEDIUM, source_keywords=[],
    )


def _nfr(nfr_id, category, linked_fr_id="FR-001"):
    return NonFunctionalRequirement(
        nfr_id=nfr_id, category=category, constraint="some constraint",
        linked_fr_id=linked_fr_id, threshold_value=None, threshold_unit=None,
    )


def _entity(entity_id, name):
    return Entity(entity_id=entity_id, name=name, attributes=[], relationships=[], source_fr_ids=[])


# =====================================================================
# stack_identifier_model.py — LLM layer
# =====================================================================

VALID_STACK_JSON = """{
  "state_management": "Zustand",
  "ui_library": "Tamagui + Victory Native",
  "backend_service": "Firebase Firestore + Cloud Functions + Stripe",
  "reasoning": ["Dashboard content needs charting", "Payments need secure backend functions"]
}"""


@patch("stack_identifier_generator.stack_identifier_model._client.chat_completion")
def test_valid_stack_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_STACK_JSON
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = identify_stack_with_llm(fr_summaries, [], 3, trace_id="t1")
    assert result is not None
    assert result["state_management"] == "Zustand"
    assert len(result["reasoning"]) == 2


@patch("stack_identifier_generator.stack_identifier_model._client.chat_completion")
def test_markdown_fenced_response_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_STACK_JSON}\n```"
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = identify_stack_with_llm(fr_summaries, [], 3, trace_id="t2")
    assert result is not None


@patch("stack_identifier_generator.stack_identifier_model._client.chat_completion")
def test_llm_api_error_returns_none(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = identify_stack_with_llm(fr_summaries, [], 3, trace_id="t3")
    assert result is None


def test_empty_fr_summaries_skips_llm_call():
    result = identify_stack_with_llm([], [], 0, trace_id="t4")
    assert result is None


@patch("stack_identifier_generator.stack_identifier_model._client.chat_completion")
def test_missing_required_key_returns_none(mock_chat):
    mock_chat.return_value = '{"state_management": "Zustand"}'  # missing ui_library, backend_service
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = identify_stack_with_llm(fr_summaries, [], 3, trace_id="t5")
    assert result is None


@patch("stack_identifier_generator.stack_identifier_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "not json"
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = identify_stack_with_llm(fr_summaries, [], 3, trace_id="t6")
    assert result is None


@patch("stack_identifier_generator.stack_identifier_model._client.chat_completion")
def test_missing_reasoning_key_defaults_to_empty_list(mock_chat):
    mock_chat.return_value = '{"state_management": "Zustand", "ui_library": "Tamagui", "backend_service": "Firestore"}'
    fr_summaries = [{"fr_id": "FR-001", "description": "x", "priority": "high"}]
    result = identify_stack_with_llm(fr_summaries, [], 3, trace_id="t7")
    assert result is not None
    assert result["reasoning"] == []


# =====================================================================
# stack_identifier.py — Stage 7 entry point
# =====================================================================

@patch("stack_identifier_generator.stack_identifier.identify_stack_with_llm")
def test_uses_llm_result_when_available(mock_identify):
    mock_identify.return_value = {
        "state_management": "Zustand",
        "ui_library": "Tamagui + Victory Native",
        "backend_service": "Firebase Firestore + Cloud Functions + Stripe",
        "reasoning": ["Custom reasoning from LLM"],
    }
    fr_set = FunctionalRequirementSet(trace_id="t8", requirements=[_fr("FR-001", "Any action")])
    nfr_set = NonFunctionalRequirementSet(trace_id="t8", requirements=[])
    entity_set = EntitySet(trace_id="t8", entities=[])
    result = identify_tech_stack(fr_set, nfr_set, entity_set, trace_id="t8")
    assert result.state_management == "Zustand"
    assert result.reasoning == ["Custom reasoning from LLM"]
    assert result.framework == "React Native (Expo)"  # always fixed regardless of LLM


@patch("stack_identifier_generator.stack_identifier.identify_stack_with_llm")
def test_falls_back_to_rules_when_llm_unavailable(mock_identify):
    mock_identify.return_value = None
    frs = [_fr(f"FR-{i:03d}", f"Action {i}") for i in range(1, 6)]
    fr_set = FunctionalRequirementSet(trace_id="t9", requirements=frs)
    nfr_set = NonFunctionalRequirementSet(trace_id="t9", requirements=[])
    entity_set = EntitySet(trace_id="t9", entities=[])
    result = identify_tech_stack(fr_set, nfr_set, entity_set, trace_id="t9")
    assert result.state_management == "Zustand"  # rule fallback: >3 FRs -> Zustand


@patch("stack_identifier_generator.stack_identifier.identify_stack_with_llm")
def test_empty_fr_list_falls_back_since_llm_skips(mock_identify):
    mock_identify.return_value = None
    fr_set = FunctionalRequirementSet(trace_id="t10", requirements=[])
    nfr_set = NonFunctionalRequirementSet(trace_id="t10", requirements=[])
    entity_set = EntitySet(trace_id="t10", entities=[])
    result = identify_tech_stack(fr_set, nfr_set, entity_set, trace_id="t10")
    assert result.framework == "React Native (Expo)"
    assert len(result.reasoning) > 0


@patch("stack_identifier_generator.stack_identifier.identify_stack_with_llm")
def test_trace_id_does_not_affect_output_shape(mock_identify):
    mock_identify.return_value = None
    fr_set = FunctionalRequirementSet(trace_id="t11", requirements=[_fr("FR-001", "Any action")])
    nfr_set = NonFunctionalRequirementSet(trace_id="t11", requirements=[_nfr("NFR-001", NFRCategory.SECURITY)])
    entity_set = EntitySet(trace_id="t11", entities=[_entity("ENT-001", "user")])
    result = identify_tech_stack(fr_set, nfr_set, entity_set, trace_id="trace-stack-999")
    assert result.navigation_library == "React Navigation"