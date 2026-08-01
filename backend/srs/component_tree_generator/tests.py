"""
tests.py — component_tree_generator

Covers: component_tree.py (Stage 6 entry point, LLM path + template
fallback) and component_tree_model.py (LLM prompt/parsing layer, per
screen). LLM calls are mocked — no real Groq API key or internet
connection needed.

Run with:
    cd backend/srs/component_tree_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from common.schemas import Sitemap, SitemapNode, ScreenType
from common.llm_client import LLMAPIError
from component_tree_generator.component_tree import generate_component_trees
from component_tree_generator.component_tree_model import generate_component_tree_with_llm


def _node(screen_id, screen_name, screen_type):
    return SitemapNode(
        screen_id=screen_id, screen_name=screen_name, route=f"/{screen_name.lower()}",
        screen_type=screen_type, linked_fr_ids=["FR-001"], is_entry_point=False,
    )


def _flatten_component_types(node_or_dict, is_dict=False):
    if is_dict:
        types = [node_or_dict["component_type"]]
        for child in node_or_dict.get("children", []):
            types.extend(_flatten_component_types(child, is_dict=True))
        return types
    types = [node_or_dict.component_type]
    for child in node_or_dict.children:
        types.extend(_flatten_component_types(child))
    return types


def _flatten_component_ids(node):
    ids = [node.component_id]
    for child in node.children:
        ids.extend(_flatten_component_ids(child))
    return ids


# =====================================================================
# component_tree_model.py — LLM layer
# =====================================================================

VALID_TREE_JSON = """{
  "component_type": "SafeAreaView",
  "props": {"style": "flex:1"},
  "design_tokens": {"spacing": "md"},
  "children": [
    {"component_type": "TextInput", "props": {"placeholder": "Email"}, "design_tokens": {}, "children": []}
  ]
}"""


@patch("component_tree_generator.component_tree_model._client.chat_completion")
def test_valid_tree_parses_correctly(mock_chat):
    mock_chat.return_value = VALID_TREE_JSON
    result = generate_component_tree_with_llm("AuthScreen", "auth", trace_id="t1")
    assert result is not None
    assert result["component_type"] == "SafeAreaView"
    assert result["children"][0]["component_type"] == "TextInput"


@patch("component_tree_generator.component_tree_model._client.chat_completion")
def test_markdown_fenced_response_still_parses(mock_chat):
    mock_chat.return_value = f"```json\n{VALID_TREE_JSON}\n```"
    result = generate_component_tree_with_llm("AuthScreen", "auth", trace_id="t2")
    assert result is not None


@patch("component_tree_generator.component_tree_model._client.chat_completion")
def test_llm_api_error_returns_none(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    result = generate_component_tree_with_llm("AuthScreen", "auth", trace_id="t3")
    assert result is None


@patch("component_tree_generator.component_tree_model._client.chat_completion")
def test_invalid_json_returns_none(mock_chat):
    mock_chat.return_value = "not json"
    result = generate_component_tree_with_llm("AuthScreen", "auth", trace_id="t4")
    assert result is None


@patch("component_tree_generator.component_tree_model._client.chat_completion")
def test_missing_component_type_returns_none(mock_chat):
    mock_chat.return_value = '{"props": {}, "children": []}'  # missing component_type
    result = generate_component_tree_with_llm("AuthScreen", "auth", trace_id="t5")
    assert result is None


@patch("component_tree_generator.component_tree_model._client.chat_completion")
def test_excessive_depth_gets_pruned(mock_chat):
    # build a deeply nested chain, 10 levels deep
    deep_node = {"component_type": "View", "props": {}, "design_tokens": {}, "children": []}
    current = deep_node
    for _ in range(10):
        child = {"component_type": "View", "props": {}, "design_tokens": {}, "children": []}
        current["children"] = [child]
        current = child

    import json
    mock_chat.return_value = json.dumps(deep_node)
    result = generate_component_tree_with_llm("AuthScreen", "auth", trace_id="t6")
    assert result is not None
    types = _flatten_component_types(result, is_dict=True)
    assert len(types) <= 7  # _MAX_DEPTH + root, pruned safely


# =====================================================================
# component_tree.py — Stage 6 entry point
# =====================================================================

@patch("component_tree_generator.component_tree.generate_component_tree_with_llm")
def test_uses_llm_result_when_available(mock_generate):
    mock_generate.return_value = {
        "component_type": "SafeAreaView", "props": {}, "design_tokens": {},
        "children": [{"component_type": "TextInput", "props": {}, "design_tokens": {}, "children": []}],
    }
    sitemap = Sitemap(trace_id="t7", nodes=[_node("SCR-001", "AuthScreen", ScreenType.AUTH)], edges=[])
    result = generate_component_trees(sitemap, trace_id="t7")
    assert len(result.trees) == 1
    assert result.trees[0].root.component_type == "SafeAreaView"
    assert result.trees[0].root.children[0].component_type == "TextInput"


@patch("component_tree_generator.component_tree.generate_component_tree_with_llm")
def test_falls_back_to_template_when_llm_unavailable(mock_generate):
    mock_generate.return_value = None
    sitemap = Sitemap(trace_id="t8", nodes=[_node("SCR-001", "AuthScreen", ScreenType.AUTH)], edges=[])
    result = generate_component_trees(sitemap, trace_id="t8")
    assert len(result.trees) == 1
    child_types = _flatten_component_types(result.trees[0].root)
    assert "TextInput" in child_types  # template builder fallback kicked in


@patch("component_tree_generator.component_tree.generate_component_tree_with_llm")
def test_component_ids_scoped_to_screen_id_on_llm_path(mock_generate):
    mock_generate.return_value = {
        "component_type": "SafeAreaView", "props": {}, "design_tokens": {},
        "children": [{"component_type": "View", "props": {}, "design_tokens": {}, "children": []}],
    }
    sitemap = Sitemap(trace_id="t9", nodes=[_node("SCR-007", "AuthScreen", ScreenType.AUTH)], edges=[])
    result = generate_component_trees(sitemap, trace_id="t9")
    all_ids = _flatten_component_ids(result.trees[0].root)
    assert all(cid.startswith("SCR-007-CMP-") for cid in all_ids)


@patch("component_tree_generator.component_tree.generate_component_tree_with_llm")
def test_mixed_screens_some_llm_some_fallback(mock_generate):
    # First screen gets LLM result, second returns None -> falls back to template
    mock_generate.side_effect = [
        {"component_type": "SafeAreaView", "props": {}, "design_tokens": {}, "children": []},
        None,
    ]
    sitemap = Sitemap(
        trace_id="t10",
        nodes=[_node("SCR-001", "AuthScreen", ScreenType.AUTH), _node("SCR-002", "MainFeed", ScreenType.FEED)],
        edges=[],
    )
    result = generate_component_trees(sitemap, trace_id="t10")
    assert len(result.trees) == 2


@patch("component_tree_generator.component_tree.generate_component_tree_with_llm")
def test_empty_sitemap_returns_empty_tree_set(mock_generate):
    sitemap = Sitemap(trace_id="t11", nodes=[], edges=[])
    result = generate_component_trees(sitemap, trace_id="t11")
    assert result.trees == []
    mock_generate.assert_not_called()


@patch("component_tree_generator.component_tree.generate_component_tree_with_llm")
def test_trace_id_propagated(mock_generate):
    mock_generate.return_value = None
    sitemap = Sitemap(trace_id="t12", nodes=[_node("SCR-001", "AuthScreen", ScreenType.AUTH)], edges=[])
    result = generate_component_trees(sitemap, trace_id="trace-tree-222")
    assert result.trace_id == "trace-tree-222"