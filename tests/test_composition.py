"""Composition contracts; no network or paid API calls."""
import sys
from pathlib import Path
import pytest
from pydantic import ValidationError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from studio.composition import Composition, default_composition, ground_composition

def test_domain_fallbacks_have_different_structure():
    flowers = default_composition("flowers", "home")
    food = default_composition("restaurant", "home")
    assert flowers["blocks"] != food["blocks"]
    assert flowers["image_ratio"] != food["image_ratio"]

def test_preserves_order_and_grounds_reference_names():
    value = {"blocks": [
        {"kind": "search", "reference_component": "SearchBar"},
        {"kind": "hero", "reference_component": "Invented"},
        {"kind": "collection", "layout": "editorial"}]}
    result = ground_composition(value, [{"name": "SearchBar"}])
    assert [b["kind"] for b in result["blocks"]] == ["search", "hero", "collection"]
    assert result["blocks"][0]["reference_component"] == "SearchBar"
    assert result["blocks"][1]["reference_component"] == ""
    assert result["blocks"][2]["layout"] == "editorial"

def test_catalog_is_not_lost_when_model_omits_collection():
    result = ground_composition({"blocks": [{"kind": "hero"}]}, [])
    assert result["blocks"][-1]["kind"] == "collection"


@pytest.mark.parametrize("prompt, layout", [
    ("A clothing shop with a horizontal collection", "rail"),
    ("A clothing shop with a mosaic layout", "mosaic"),
    ("A clothing shop with a list layout", "cards"),
])
def test_same_business_can_have_different_prompt_driven_structures(prompt, layout):
    fallback = default_composition("clothing", "home", prompt=prompt)
    assert next(b for b in fallback["blocks"] if b["kind"] == "collection")["layout"] == layout
    planned = ground_composition({"blocks": [{"kind": "collection"}]}, [], prompt)
    assert planned["blocks"][0]["layout"] == layout


def test_layout_examples_use_training_split_and_matching_screens():
    from studio.design_retrieval import retrieve_layout_examples
    examples = retrieve_layout_examples("luxury jewellery", {
        "business": "jewellery", "style": "luxury", "pages": ["home", "products"]
    })
    assert len(examples) == 4
    assert {r["page"] for r in examples} == {"home", "products"}
    assert all(r["business"] == "jewellery" for r in examples)


def test_category_tiles_are_valid_and_legacy_defaults_work():
    assert ground_composition({"blocks": [{"kind": "collection"}]}, [], "Use category tiles")["category_style"] == "tiles"
    assert Composition.model_validate({"blocks": [{"kind": "collection"}]}).category_style == "chips"


def test_negative_layout_request_does_not_force_that_layout():
    plan = ground_composition({"blocks": [{"kind": "collection", "layout": "grid"}]}, [], "No carousel. Avoid mosaic.")
    assert plan["blocks"][0]["layout"] == "grid"

@pytest.mark.parametrize("value", [
    {"blocks": [{"kind": "execute_script"}]},
    {"blocks": [{"kind": "hero", "code": "alert(1)"}]},
    {"blocks": [{"kind": "hero"}] * 9},
])
def test_rejects_unsupported_model_output(value):
    with pytest.raises(ValidationError):
        Composition.model_validate(value)
