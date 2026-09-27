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

@pytest.mark.parametrize("value", [
    {"blocks": [{"kind": "execute_script"}]},
    {"blocks": [{"kind": "hero", "code": "alert(1)"}]},
    {"blocks": [{"kind": "hero"}] * 9},
])
def test_rejects_unsupported_model_output(value):
    with pytest.raises(ValidationError):
        Composition.model_validate(value)
