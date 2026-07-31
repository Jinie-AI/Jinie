"""
tests.py — entities_generator

Covers: entities.py (Stage 5 entry point, LLM path + rule fallback)
and entities_model.py (LLM prompt/parsing layer). LLM calls are
mocked — no real Groq API key or internet connection needed.

Run with:
    cd backend/srs/entities_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import (
    RawRequirementFeatures,
    SupportedLanguage,
    FunctionalRequirement,
    FunctionalRequirementSet,
    Priority,
)
from common.llm_client import LLMAPIError
from entities_generator.entities import generate_entities
from entities_generator.entities_model import generate_entities_with_llm


def _raw_features(candidate_entities, keywords=None, normalized_text="test prompt"):
    return RawRequirementFeatures(
        trace_id="test-trace",
        original_prompt=normalized_text,
        detected_language=SupportedLanguage.ENGLISH,
        normalized_text=normalized_text,
        extracted_keywords=keywords or [],
        intent_tags=[],
        candidate_entities=candidate_entities,
        confidence_score=0.8,
    )


def _fr_set(descriptions):
    frs = [
        FunctionalRequirement(
            fr_id=f"FR-{i+1:03d}", description=desc, actors=["User"],
            inputs=[], outputs=[], priority=Priority.MEDIUM, source_keywords=[],
        )
        for i, desc in enumerate(descriptions)
    ]
    return FunctionalRequirementSet(trace_id="test-trace", requirements=frs)


# =====================================================================
# entities_model.py — LLM layer
# =====================================================================

VALID_ENTITIES_JSON = """[
  {
    "name": "user",
    "attributes": [
      {"name": "user_id", "type": "string", "required": true},
      {"name": "email", "type": "string", "required": true}
    ],
    "relationships": []
  },
  {
    "name": "post",
    "attributes": [
      {"name": "post_id", "type": "string", "required": true},
      {"name": "author_id", "type": "reference", "required": true}
    ],
    "relationships": [{"to_entity": "user", "relationship_type": "one_to_many"}]
  }
]"""


@patch("entities_generator.entities_model._client.chat_completion")
def test_valid_entities_parse_correctly(mock_chat):
    mock_chat.return_value = VALID_ENTITIES_JSON
    result = generate_entities_with_llm("an app with users and posts", [{"fr_id": "FR-001", "description": "x"}], trace_id="t1")
    assert result is not None
    assert len(result) == 2
    assert result[1]["relationships"][0]["to_entity"] == "user"


@patch("entities_generator.entities_model._client.chat_completion")
def test_markdown_fenced_response_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_ENTITIES_JSON}\n```"
    result = generate_entities_with_llm("some prompt", [], trace_id="t2")
    assert result is not None
    assert len(result) == 2


@patch("entities_generator.entities_model._client.chat_completion")
def test_llm_api_error_returns_none(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    result = generate_entities_with_llm("some prompt", [], trace_id="t3")
    assert result is None


@patch("entities_generator.entities_model._client.chat_completion")
def test_non_array_response_returns_none(mock_chat):
    mock_chat.return_value = '{"not": "an array"}'
    result = generate_entities_with_llm("some prompt", [], trace_id="t4")
    assert result is None


@patch("entities_generator.entities_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "not json"
    result = generate_entities_with_llm("some prompt", [], trace_id="t5")
    assert result is None


@patch("entities_generator.entities_model._client.chat_completion")
def test_invalid_attribute_type_defaults_to_string(mock_chat):
    mock_chat.return_value = """[
      {"name": "widget", "attributes": [{"name": "field", "type": "not_real_type", "required": true}], "relationships": []}
    ]"""
    result = generate_entities_with_llm("some prompt", [], trace_id="t6")
    assert result is not None
    assert result[0]["attributes"][0]["type"] == "string"


@patch("entities_generator.entities_model._client.chat_completion")
def test_relationship_to_unknown_entity_is_dropped(mock_chat):
    mock_chat.return_value = """[
      {"name": "post", "attributes": [], "relationships": [{"to_entity": "ghost_entity", "relationship_type": "one_to_many"}]}
    ]"""
    result = generate_entities_with_llm("some prompt", [], trace_id="t7")
    assert result is not None
    assert result[0]["relationships"] == []


@patch("entities_generator.entities_model._client.chat_completion")
def test_malformed_item_is_skipped_not_fatal(mock_chat):
    mock_chat.return_value = """[
      {"name": "user", "attributes": [], "relationships": []},
      {"missing_name_key": true}
    ]"""
    result = generate_entities_with_llm("some prompt", [], trace_id="t8")
    assert result is not None
    assert len(result) == 1


@patch("entities_generator.entities_model._client.chat_completion")
def test_empty_array_returns_none(mock_chat):
    mock_chat.return_value = "[]"
    result = generate_entities_with_llm("some prompt", [], trace_id="t9")
    assert result is None


# =====================================================================
# entities.py — Stage 5 entry point
# =====================================================================

@patch("entities_generator.entities.generate_entities_with_llm")
def test_uses_llm_result_when_available(mock_generate):
    mock_generate.return_value = [
        {"name": "user", "attributes": [{"name": "user_id", "type": "string", "required": True}], "relationships": []},
    ]
    raw = _raw_features(candidate_entities=["user"])
    fr_set = _fr_set(["User logs in"])
    result = generate_entities(raw, fr_set, trace_id="t10")
    assert len(result.entities) == 1
    assert result.entities[0].name == "user"
    assert result.entities[0].entity_id == "ENT-001"


@patch("entities_generator.entities.generate_entities_with_llm")
def test_falls_back_to_rules_when_llm_unavailable(mock_generate):
    mock_generate.return_value = None
    raw = _raw_features(candidate_entities=["user"])
    fr_set = _fr_set(["User logs in"])
    result = generate_entities(raw, fr_set, trace_id="t11")
    entity_names = [e.name for e in result.entities]
    assert "user" in entity_names  # archetype dictionary fallback kicked in


@patch("entities_generator.entities.generate_entities_with_llm")
def test_relationship_filtered_if_target_not_in_llm_set(mock_generate):
    mock_generate.return_value = [
        {"name": "post", "attributes": [], "relationships": [{"to_entity": "nonexistent", "relationship_type": "one_to_many"}]},
    ]
    raw = _raw_features(candidate_entities=["post"])
    fr_set = _fr_set(["User creates post"])
    result = generate_entities(raw, fr_set, trace_id="t12")
    assert result.entities[0].relationships == []


@patch("entities_generator.entities.generate_entities_with_llm")
def test_empty_candidates_and_llm_unavailable_returns_empty(mock_generate):
    mock_generate.return_value = None
    raw = _raw_features(candidate_entities=[])
    fr_set = _fr_set(["A completely generic action with no entity nouns"])
    result = generate_entities(raw, fr_set, trace_id="t13")
    assert result.entities == []


@patch("entities_generator.entities.generate_entities_with_llm")
def test_trace_id_propagated(mock_generate):
    mock_generate.return_value = None
    raw = _raw_features(candidate_entities=["user"])
    fr_set = _fr_set(["User logs in"])
    result = generate_entities(raw, fr_set, trace_id="trace-entities-333")
    assert result.trace_id == "trace-entities-333"