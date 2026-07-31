"""
tests.py — sitemap_generator

Covers: sitemap.py (Stage 4 entry point, LLM path + rule fallback) and
sitemap_model.py (LLM prompt/parsing layer). LLM calls are mocked —
no real Groq API key or internet connection needed.

Run with:
    cd backend/srs/sitemap_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import (
    FunctionalRequirement,
    FunctionalRequirementSet,
    Priority,
    ScreenType,
)
from common.llm_client import LLMAPIError
from sitemap_generator.sitemap import generate_sitemap
from sitemap_generator.sitemap_model import generate_sitemap_with_llm


def _fr(fr_id, description, inputs=None, outputs=None):
    return FunctionalRequirement(
        fr_id=fr_id,
        description=description,
        actors=["User"],
        inputs=inputs or [],
        outputs=outputs or [],
        priority=Priority.HIGH,
        source_keywords=[],
    )


# =====================================================================
# sitemap_model.py — LLM layer
# =====================================================================

VALID_SITEMAP_JSON = """{
  "screens": [
    {"screen_name": "AuthScreen", "route": "/auth", "screen_type": "auth", "linked_fr_ids": ["FR-001"], "is_entry_point": true},
    {"screen_name": "MainFeed", "route": "/feed", "screen_type": "feed", "linked_fr_ids": ["FR-002"], "is_entry_point": false}
  ],
  "edges": [
    {"from_screen": "AuthScreen", "to_screen": "MainFeed", "trigger": "on_login_success"}
  ]
}"""


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_valid_sitemap_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_SITEMAP_JSON
    fr_summaries = [{"fr_id": "FR-001", "description": "login"}, {"fr_id": "FR-002", "description": "feed"}]
    result = generate_sitemap_with_llm(fr_summaries, trace_id="t1")
    assert result is not None
    assert len(result["screens"]) == 2
    assert len(result["edges"]) == 1
    assert result["screens"][0]["is_entry_point"] is True


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_markdown_fenced_response_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_SITEMAP_JSON}\n```"
    fr_summaries = [{"fr_id": "FR-001", "description": "login"}]
    result = generate_sitemap_with_llm(fr_summaries, trace_id="t2")
    assert result is not None


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_llm_api_error_returns_none(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    fr_summaries = [{"fr_id": "FR-001", "description": "login"}]
    result = generate_sitemap_with_llm(fr_summaries, trace_id="t3")
    assert result is None


def test_empty_fr_summaries_skips_llm_call():
    result = generate_sitemap_with_llm([], trace_id="t4")
    assert result is None


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_missing_screens_key_returns_none(mock_chat):
    mock_chat.return_value = '{"edges": []}'
    fr_summaries = [{"fr_id": "FR-001", "description": "login"}]
    result = generate_sitemap_with_llm(fr_summaries, trace_id="t5")
    assert result is None


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_invalid_screen_type_falls_back_to_generic(mock_chat):
    mock_chat.return_value = """{
      "screens": [{"screen_name": "Weird", "route": "/x", "screen_type": "not_real", "linked_fr_ids": [], "is_entry_point": false}],
      "edges": []
    }"""
    result = generate_sitemap_with_llm([{"fr_id": "FR-001", "description": "x"}], trace_id="t6")
    assert result is not None
    assert result["screens"][0]["screen_type"] == "generic"


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_edge_referencing_unknown_screen_is_dropped(mock_chat):
    mock_chat.return_value = """{
      "screens": [{"screen_name": "AuthScreen", "route": "/auth", "screen_type": "auth", "linked_fr_ids": [], "is_entry_point": true}],
      "edges": [{"from_screen": "AuthScreen", "to_screen": "GhostScreen", "trigger": "navigate"}]
    }"""
    result = generate_sitemap_with_llm([{"fr_id": "FR-001", "description": "x"}], trace_id="t7")
    assert result is not None
    assert result["edges"] == []


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_unknown_fr_id_in_linked_ids_is_filtered(mock_chat):
    mock_chat.return_value = """{
      "screens": [{"screen_name": "AuthScreen", "route": "/auth", "screen_type": "auth", "linked_fr_ids": ["FR-999"], "is_entry_point": true}],
      "edges": []
    }"""
    result = generate_sitemap_with_llm([{"fr_id": "FR-001", "description": "x"}], trace_id="t8")
    assert result is not None
    assert result["screens"][0]["linked_fr_ids"] == []


@patch("sitemap_generator.sitemap_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "not json"
    result = generate_sitemap_with_llm([{"fr_id": "FR-001", "description": "x"}], trace_id="t9")
    assert result is None


# =====================================================================
# sitemap.py — Stage 4 entry point
# =====================================================================

@patch("sitemap_generator.sitemap.generate_sitemap_with_llm")
def test_uses_llm_result_when_available(mock_generate):
    mock_generate.return_value = {
        "screens": [
            {"screen_name": "AuthScreen", "route": "/auth", "screen_type": "auth", "linked_fr_ids": ["FR-001"], "is_entry_point": True},
        ],
        "edges": [],
    }
    fr_set = FunctionalRequirementSet(trace_id="t10", requirements=[_fr("FR-001", "User logs in")])
    result = generate_sitemap(fr_set, trace_id="t10")
    assert len(result.nodes) == 1
    assert result.nodes[0].screen_name == "AuthScreen"
    assert result.nodes[0].screen_type == ScreenType.AUTH


@patch("sitemap_generator.sitemap.generate_sitemap_with_llm")
def test_falls_back_to_rules_when_llm_unavailable(mock_generate):
    mock_generate.return_value = None
    fr_set = FunctionalRequirementSet(trace_id="t11", requirements=[_fr("FR-001", "User logs in with password", outputs=["auth_token"])])
    result = generate_sitemap(fr_set, trace_id="t11")
    screen_names = [n.screen_name for n in result.nodes]
    assert "AuthScreen" in screen_names  # keyword-lookup fallback kicked in


@patch("sitemap_generator.sitemap.generate_sitemap_with_llm")
def test_llm_result_with_no_entry_point_gets_one_assigned(mock_generate):
    mock_generate.return_value = {
        "screens": [
            {"screen_name": "SomeScreen", "route": "/x", "screen_type": "generic", "linked_fr_ids": [], "is_entry_point": False},
        ],
        "edges": [],
    }
    fr_set = FunctionalRequirementSet(trace_id="t12", requirements=[_fr("FR-001", "Some action")])
    result = generate_sitemap(fr_set, trace_id="t12")
    assert any(n.is_entry_point for n in result.nodes)


@patch("sitemap_generator.sitemap.generate_sitemap_with_llm")
def test_empty_fr_list_returns_empty_sitemap(mock_generate):
    mock_generate.return_value = None
    fr_set = FunctionalRequirementSet(trace_id="t13", requirements=[])
    result = generate_sitemap(fr_set, trace_id="t13")
    assert result.nodes == []
    assert result.edges == []


@patch("sitemap_generator.sitemap.generate_sitemap_with_llm")
def test_trace_id_propagated(mock_generate):
    mock_generate.return_value = None
    fr_set = FunctionalRequirementSet(trace_id="t14", requirements=[_fr("FR-001", "User logs in", outputs=["auth_token"])])
    result = generate_sitemap(fr_set, trace_id="trace-sitemap-555")
    assert result.trace_id == "trace-sitemap-555"