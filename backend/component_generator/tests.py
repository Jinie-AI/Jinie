"""
tests.py — component_generator

Covers: generator.py (Stage 5 entry point + rule-based fallback),
generator_model.py (LLM prompt/parsing layer), and
generator_validator.py (post-generation validation rules). All
network calls are mocked — no real Groq API key or internet
connection needed.

Run with:
    cd backend/component_generator
    python -m pytest tests.py -v
"""

import pytest
from unittest.mock import patch

from generator import ComponentGenerator
from generator_model import generate_component_with_llm
from generator_validator import validate_generated_code
from exceptions import (
    MissingComponentNameError,
    InvalidDesignTokensError,
    InvalidLayoutSpecificationError,
    UnsupportedComponentTypeError,
    MalformedHierarchyError,
    ComponentValidationError,
    ComponentGenerationError,
)
from shared.llm_client import LLMAPIError


SIMPLE_TREE = {
    "type": "Card",
    "padding": 16,
    "children": [
        {"type": "Button", "props": {"label": "Continue"}},
    ],
}

SIMPLE_TOKENS = {
    "colors": {"surface": "#FFFFFF", "onPrimary": "#111111"},
    "typography": {"fontSize": 14, "fontWeight": "500"},
    "spacing": {"default": 8},
}

VALID_AI_CODE = """import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const WelcomeCard = () => {
  return (
    <View style={styles.root}>
      <TouchableOpacity style={styles.root_0}>
        <Text style={styles.root_0_label}>Continue</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  root: { padding: 16 },
  root_0: { padding: 8 },
  root_0_label: { fontSize: 14 }
});

export default WelcomeCard;
"""


# =====================================================================
# generator_model.py — LLM layer
# =====================================================================

@patch("generator_model._client.chat_completion")
def test_llm_returns_cleaned_code_on_success(mock_chat):
    mock_chat.return_value = VALID_AI_CODE
    result = generate_component_with_llm("WelcomeCard", SIMPLE_TREE, SIMPLE_TOKENS, trace_id="t1")
    assert result is not None
    assert "export default WelcomeCard" in result


@patch("generator_model._client.chat_completion")
def test_llm_response_wrapped_in_markdown_fences_still_parses(mock_chat):
    mock_chat.return_value = f"```jsx\n{VALID_AI_CODE}\n```"
    result = generate_component_with_llm("WelcomeCard", SIMPLE_TREE, SIMPLE_TOKENS, trace_id="t2")
    assert result is not None
    assert "```" not in result


@patch("generator_model._client.chat_completion")
def test_llm_api_error_returns_none_not_raise(mock_chat):
    mock_chat.side_effect = LLMAPIError("network down")
    result = generate_component_with_llm("WelcomeCard", SIMPLE_TREE, SIMPLE_TOKENS, trace_id="t3")
    assert result is None


@patch("generator_model._client.chat_completion")
def test_llm_empty_response_returns_none(mock_chat):
    mock_chat.return_value = "   "
    result = generate_component_with_llm("WelcomeCard", SIMPLE_TREE, SIMPLE_TOKENS, trace_id="t4")
    assert result is None


# =====================================================================
# generator_validator.py — validation rules
# =====================================================================

def test_valid_code_passes_validation():
    validate_generated_code(VALID_AI_CODE, "WelcomeCard", trace_id="t5")  # should not raise


def test_empty_code_fails_validation():
    with pytest.raises(ComponentValidationError):
        validate_generated_code("", "WelcomeCard", trace_id="t6")


def test_code_missing_import_fails_validation():
    code = "const WelcomeCard = () => <View />;\nexport default WelcomeCard;"
    with pytest.raises(ComponentValidationError):
        validate_generated_code(code, "WelcomeCard", trace_id="t7")


def test_code_missing_default_export_fails_validation():
    code = "import React from 'react';\nconst WelcomeCard = () => <View />;"
    with pytest.raises(ComponentValidationError):
        validate_generated_code(code, "WelcomeCard", trace_id="t8")


def test_code_referencing_wrong_component_name_fails_validation():
    with pytest.raises(ComponentValidationError):
        validate_generated_code(VALID_AI_CODE, "SomeOtherName", trace_id="t9")


def test_code_with_unbalanced_brackets_fails_validation():
    code = "import React from 'react';\nconst WelcomeCard = () => {\nexport default WelcomeCard;"
    with pytest.raises(ComponentValidationError):
        validate_generated_code(code, "WelcomeCard", trace_id="t10")


# =====================================================================
# generator.py — Stage 5 entry point
# =====================================================================

@patch("generator.generate_component_with_llm")
def test_uses_ai_result_when_available_and_valid(mock_generate):
    mock_generate.return_value = VALID_AI_CODE
    generator = ComponentGenerator()

    result = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, SIMPLE_TREE, trace_id="t11")

    assert "export default WelcomeCard" in result
    assert "Traceability-ID" in result


@patch("generator.generate_component_with_llm")
def test_falls_back_to_rule_based_renderer_when_llm_unavailable(mock_generate):
    mock_generate.return_value = None
    generator = ComponentGenerator()

    result = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, SIMPLE_TREE, trace_id="t12")

    assert "export default WelcomeCard" in result
    assert "StyleSheet.create" in result
    assert "Traceability-ID" in result


@patch("generator.generate_component_with_llm")
def test_falls_back_to_rule_based_renderer_when_ai_output_fails_validation(mock_generate):
    mock_generate.return_value = "not real component code at all"
    generator = ComponentGenerator()

    result = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, SIMPLE_TREE, trace_id="t13")

    assert "export default WelcomeCard" in result
    assert "StyleSheet.create" in result


@patch("generator.generate_component_with_llm")
def test_trace_id_is_auto_generated_when_not_provided(mock_generate):
    mock_generate.return_value = VALID_AI_CODE
    generator = ComponentGenerator()

    result = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, SIMPLE_TREE)

    assert "export default WelcomeCard" in result


@patch("generator.generate_component_with_llm")
def test_traceability_id_is_deterministic_for_same_inputs(mock_generate):
    mock_generate.return_value = None  # force rule-based path (deterministic, easy to compare)
    generator = ComponentGenerator()

    result_1 = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, SIMPLE_TREE, trace_id="tA")
    result_2 = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, SIMPLE_TREE, trace_id="tB")

    id_1 = result_1.splitlines()[0]
    id_2 = result_2.splitlines()[0]
    assert id_1 == id_2  # same component inputs -> same Traceability-ID, regardless of trace_id


# =====================================================================
# generator.py — input validation (unchanged contract)
# =====================================================================

def test_raises_on_empty_component_name():
    generator = ComponentGenerator()
    with pytest.raises(MissingComponentNameError):
        generator.generate_component("", SIMPLE_TOKENS, SIMPLE_TREE)


def test_raises_on_component_name_not_starting_with_letter():
    generator = ComponentGenerator()
    with pytest.raises(MissingComponentNameError):
        generator.generate_component("1Card", SIMPLE_TOKENS, SIMPLE_TREE)


def test_raises_on_non_dict_design_tokens():
    generator = ComponentGenerator()
    with pytest.raises(InvalidDesignTokensError):
        generator.generate_component("WelcomeCard", "not-a-dict", SIMPLE_TREE)


def test_raises_on_missing_layout_type():
    generator = ComponentGenerator()
    with pytest.raises(InvalidLayoutSpecificationError):
        generator.generate_component("WelcomeCard", SIMPLE_TOKENS, {"children": []})


@patch("generator.generate_component_with_llm")
def test_unsupported_component_type_falls_back_to_generic_view(mock_generate):
    """Unknown component_type values (e.g. real SRS types like SearchBar,
    FlatList) should no longer crash the fallback renderer — they render
    as a generic View instead, since the fallback's job is to never
    block generation, not to be pixel-perfect for every type."""
    mock_generate.return_value = None  # force the rule-based fallback path
    generator = ComponentGenerator()

    result = generator.generate_component("WelcomeCard", SIMPLE_TOKENS, {"type": "VideoPlayer"})

    assert "export default WelcomeCard" in result
    assert "<View" in result


def test_raises_on_malformed_children():
    generator = ComponentGenerator()
    with pytest.raises(MalformedHierarchyError):
        generator.generate_component("WelcomeCard", SIMPLE_TOKENS, {"type": "Card", "children": "not-a-list"})


def test_raises_on_excessive_nesting_depth():
    generator = ComponentGenerator()
    node = {"type": "Container"}
    current = node
    for _ in range(30):
        child = {"type": "Container"}
        current["children"] = [child]
        current = child

    with pytest.raises(MalformedHierarchyError):
        generator.generate_component("WelcomeCard", SIMPLE_TOKENS, node)


# =====================================================================
# generator.py — real SRS fixture data (component_type field, unknown types)
# =====================================================================

import json
import os

_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "sample_component_trees.json")


def _load_real_sample_trees():
    with open(_FIXTURE_PATH) as f:
        return json.load(f)["trees"]


@patch("generator.generate_component_with_llm")
def test_generates_from_real_srs_tree_with_component_type_field(mock_generate):
    """Real SRS ComponentNode data uses 'component_type', not 'type', and
    includes node types (SafeAreaView, SearchBar, FlatList, ItemCard)
    this module never explicitly modeled. This should work end-to-end
    without raising, whether the AI succeeds or falls back."""
    mock_generate.return_value = None  # force rule-based fallback for a deterministic assertion
    trees = _load_real_sample_trees()
    product_catalog_tree = next(t for t in trees if t["screen_name"] == "ProductCatalog")

    generator = ComponentGenerator()
    result = generator.generate_component(
        "ProductCatalogScreen",
        {"colors": {"surface": "#FFFFFF"}},
        product_catalog_tree["root"],
    )

    assert "export default ProductCatalogScreen" in result
    assert "Traceability-ID" in result


@patch("generator.generate_component_with_llm")
def test_generates_all_screens_from_real_srs_output(mock_generate):
    """Confirms every screen in a real multi-screen SRS output can be
    generated without any single node type crashing the pipeline."""
    mock_generate.return_value = None
    trees = _load_real_sample_trees()

    generator = ComponentGenerator()
    for tree in trees:
        component_name = f"{tree['screen_name']}Screen"
        result = generator.generate_component(
            component_name,
            {"colors": {"surface": "#F5F5F5"}, "spacing": {"default": 12}},
            tree["root"],
        )
        assert f"export default {component_name}" in result