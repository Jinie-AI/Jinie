"""Planning and export regressions. API responses are mocked; no paid calls."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from studio import openai_planner as planner
from studio.screen_contract import normalize_pages

BASE = {
    "business": "beauty",
    "pages": ["home"],
    "style": "minimal",
    "features": [],
    "warnings": [],
    "source": "DistilBERT",
}


def mock_response(monkeypatch, plan=None, refusal=None):
    import openai

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-never-real")
    client = MagicMock()
    client.beta.chat.completions.parse.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(parsed=plan, refusal=refusal))
        ],
        usage=None,
    )
    factory = MagicMock()
    factory.return_value.__enter__.return_value = client
    monkeypatch.setattr(openai, "OpenAI", factory)
    return client


def make_plan(**changes):
    return planner.Plan(
        **{
            "business": "clothing",
            "pages": ["products", "checkout"],
            "style": "minimal",
            "summary": "A clothing demo.",
            "questions": [],
            "unsupported_features": [],
            **changes,
        }
    )


def test_no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(planner.PlannerError, match="Set OPENAI_API_KEY"):
        planner.plan_requirements("clothing store", "", BASE)


def test_api_custom_screen_survives_with_requested_fields(monkeypatch):
    response = make_plan(pages=["home", "products", "profile", "settings", "custom_medical_record"], screen_configs=[{
        "page": "custom_medical_record", "title": "Medical Record",
        "sections": [{"title": "Record", "fields": [{"label": "Patient name", "value": "Invented person"}]}]
    }])
    mock_response(monkeypatch, response)
    spec, _ = planner.plan_requirements(
        "Makeup app with homescreen, menu screen, user profile. Dont add settings. Medical record with patient name, patient id, patient condition, skin colour.", "", BASE)
    assert set(spec["pages"]) == {"home", "products", "profile", "custom_medical_record"}
    fields = [f for s in spec["screen_configs"]["custom_medical_record"]["sections"] for f in s["fields"]]
    assert {f["label"] for f in fields} == {"Patient name", "Patient ID", "Patient condition", "Skin colour"}
    assert all(f["value"] == "" for f in fields)
    assert "skin colour" in spec["page_requirements"]["custom_medical_record"].lower()


def test_api_plan_grounding_and_provenance(monkeypatch):
    plan = make_plan(unsupported_features=["Online payments"])
    client = mock_response(monkeypatch, plan)
    refs = [
        {
            "name": "Card",
            "description": "Product card",
            "props": ["children"],
            "screens": ["products"],
            "score": 0.4,
        }
    ]
    local = {
        **BASE,
        "layout_recommendations": [
            {
                "id": "editorial",
                "source": "synthetic-trained Random Forest",
                "score": 0.7,
            }
        ],
    }
    spec, meta = planner.plan_requirements(
        "clothing store", "reference", local, rag_components=refs
    )
    assert set(spec["pages"]) == {"products", "detail", "checkout", "cart"}
    assert meta["local_prediction"]["business"] == "beauty"
    assert meta["provider"] == planner.configuration()["provider"]
    assert meta["unsupported_features"] == ["Online payments"]
    assert any("Online payments" in warning for warning in spec["warnings"])
    kwargs = client.beta.chat.completions.parse.call_args.kwargs
    assert kwargs["store"] is False and kwargs["response_format"] is planner.Plan
    payload = json.loads(kwargs["messages"][1]["content"])
    assert payload["retrieved_ui_components"] == refs
    assert (
        payload["local_suggestions"]["layout_recommendations"][0]["id"] == "editorial"
    )
    assert "settings" in payload["supported_screen_behaviors"]
    assert "test-key-never-real" not in json.dumps(meta)


@pytest.mark.parametrize("refusal", [None, "Cannot process this request"])
def test_missing_plan_or_refusal(monkeypatch, refusal):
    mock_response(monkeypatch, refusal=refusal)
    with pytest.raises(planner.PlannerError):
        planner.plan_requirements("clothing store", "", BASE)


def test_error_redaction(monkeypatch):
    import openai

    monkeypatch.setenv("OPENAI_API_KEY", "private-test-value")
    monkeypatch.setattr(
        openai, "OpenAI", MagicMock(side_effect=RuntimeError("private-test-value"))
    )
    with pytest.raises(planner.PlannerError) as exc:
        planner.plan_requirements("clothing store", "", BASE)
    assert "private-test-value" not in str(exc.value)


def test_screen_schema_matches_renderer():
    from studio.api import Requirement, Review
    from studio.screen_contract import CAPABILITIES

    plan = make_plan(business="flowers", pages=list(CAPABILITIES))
    assert len(plan.pages) == 10
    for page in CAPABILITIES:
        Requirement(id="REQ-001", page=page, text="A valid screen requirement")
    with pytest.raises(ValueError):
        make_plan(pages=["tracking"])
    with pytest.raises(ValueError):
        Review(requirements=[], design={}, business="unknown")


@pytest.mark.parametrize(
    "prompt",
    [
        "No cart and no search",
        "I don't want a shopping bag or search. No search.",
        "cart nahi chahiye, search nahi",
    ],
)
def test_exclusions_survive_planner(monkeypatch, prompt):
    plan = make_plan(
        pages=["home", "products", "cart", "checkout", "search"],
        screen_configs=[
            planner.ScreenConfig(
                page="home",
                show_search=True,
                reference_components=["Card", "ImaginaryWidget"],
            ),
        ],
    )
    mock_response(monkeypatch, plan)
    spec, _ = planner.plan_requirements(prompt, "", BASE, [{"name": "Card"}])
    assert not {"cart", "checkout", "search"} & set(spec["pages"])
    assert spec["screen_configs"]["home"]["show_search"] is False
    assert spec["screen_configs"]["home"]["reference_components"] == ["Card"]


def test_requested_optional_screens_survive_local_labels():
    assert {"settings", "profile"} <= set(
        normalize_pages(["home"], "Include settings and profile")
    )


def test_product_urls_use_catalog_not_invented_photography(monkeypatch):
    plan = make_plan(
        business="flowers",
        products=[
            planner.Product(
                name="Rose bouquet",
                price=2500,
                description="Sample bouquet",
                category="Roses",
                icon="*",
                image_url="https://invalid.example/invented.png",
            )
        ],
    )
    mock_response(monkeypatch, plan)
    spec, _ = planner.plan_requirements("A flower shop", "", BASE)
    assert spec["products"][0]["image_url"] in {
        p["image_url"] for p in planner.products("flowers")
    }
    with pytest.raises(ValueError):
        planner.Product(
            name="x", price=float("nan"), description="x", category="x", icon="x"
        )


def test_route_passes_both_models_and_retrieval(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from studio import api

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(api.models, "intake", lambda _: dict(BASE))
    recommendation = [{"id": "editorial", "score": 0.8, "source": "test layout model"}]
    monkeypatch.setattr(api.models, "recommend", lambda *args: recommendation)
    monkeypatch.setattr(api.store, "save", lambda p: None)
    fn = MagicMock(
        return_value=(
            {**BASE, "business": "clothing"},
            {
                "model": "test",
                "summary": "x",
                "questions": [],
                "unsupported_features": [],
            },
        )
    )
    monkeypatch.setattr(api.openai_planner, "plan_requirements", fn)
    app = FastAPI()
    app.include_router(api.router)
    client = TestClient(app)
    assert (
        client.post(
            "/api/projects", json={"prompt": "Make a clothing shop"}
        ).status_code
        == 201
    )
    fn.assert_not_called()
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    result = client.post("/api/projects", json={"prompt": "Make a clothing shop"})
    assert result.status_code == 201
    assert fn.call_args.args[2]["source"] == "DistilBERT"
    assert fn.call_args.args[2]["layout_recommendations"] == recommendation
    assert fn.call_args.kwargs["rag_components"]
    fn.side_effect = planner.PlannerError("Planning unavailable")
    assert (
        client.post(
            "/api/projects", json={"prompt": "Make a clothing shop"}
        ).status_code
        == 502
    )


def test_custom_catalog_and_references_reach_export(monkeypatch, tmp_path):
    from studio import compiler, store

    monkeypatch.setattr(store, "DATA", tmp_path)
    monkeypatch.setattr(compiler, "code_candidate", lambda _: None)
    product = {
        "id": "sample-1",
        "name": "Telescope",
        "price": 12000,
        "description": "Sample product",
        "category": "Astronomy",
        "icon": "*",
    }
    p = {
        "id": "a" * 32,
        "name": "Star Shop",
        "spec": {
            "business": "electronics",
            "business_label": "astronomy",
            "features": ["catalog"],
            "products": [product],
        },
        "design": {
            "primary": "#112233",
            "theme": "light",
            "font": "sans",
            "layout": "grid",
        },
        "requirements": [{"id": "REQ-001", "page": "products", "approved": True}],
        "model_warnings": [],
        "screen_configs": {
            "products": {
                "title": "Explore space",
                "layout": "editorial",
                "show_search": False,
            }
        },
        "rag_components": [{"name": "Card", "screens": ["products"], "score": 0.4}],
    }
    compiler.compile_project(p)
    config = json.loads(
        (store.folder(p["id"]) / "source/src/config.json").read_text(encoding="utf-8")
    )
    assert config["products"] == [product] and config["business"] == "astronomy"
    assert config["screen_configs"]["products"]["show_search"] is False
    assert p["components"][-1]["used"] is False
    assert p["traceability"][0]["references"] == ["RAG-001"]
    compiler.bundle(p)
    assert (store.folder(p["id"]) / p["_pending_preview"] / "index.html").exists()


def test_refine_design_updates_existing_project(monkeypatch):
    from studio import api

    project = {
        "id": "x",
        "prompt": "A clothing shop",
        "revision": 1,
        "status": "ready",
        "spec": dict(BASE),
        "design": {"primary": "#112233"},
        "screen_configs": {},
        "events": [],
        "rag_components": [],
    }
    monkeypatch.setattr(api, "mutable", lambda _: project)
    monkeypatch.setattr(api.store, "save", lambda p: None)
    monkeypatch.setattr(
        api.openai_planner, "configuration", lambda: {"configured": True}
    )
    monkeypatch.setattr(
        api.openai_planner,
        "plan_requirements",
        lambda *args, **kwargs: (
            {
                "design": {"primary": "#994422"},
                "screen_configs": {
                    "home": {"title": "Warm essentials", "layout": "editorial"}
                },
            },
            {
                "summary": "Updated appearance",
                "questions": [],
                "unsupported_features": [],
            },
        ),
    )
    result = api.refine_design(
        "x", api.RefineDesign(instructions="Use warm terracotta colors")
    )
    assert result["design"]["primary"] == "#994422"
    assert result["screen_configs"]["home"]["title"] == "Warm essentials"
    assert result["revision"] == 2 and result["status"] == "review"
    assert result["spec"]["pages"] == ["home"]


def test_api_composition_survives_planning(monkeypatch):
    composition = {
        "hero_style": "split",
        "density": "airy",
        "blocks": [
            {"kind": "search", "reference_component": "SearchBar"},
            {"kind": "hero", "title": "Weekend essentials"},
            {"kind": "collection", "layout": "editorial"},
        ],
    }
    plan = make_plan(pages=["home", "products"], screen_configs=[
        planner.ScreenConfig(page="home", composition=composition)
    ])
    mock_response(monkeypatch, plan)
    refs = [{"name": "SearchBar", "description": "Search", "props": [], "screens": ["home"]}]
    spec, _ = planner.plan_requirements("Editorial store with search first", "", BASE, rag_components=refs)
    saved = spec["screen_configs"]["home"]["composition"]
    assert saved["hero_style"] == "split"
    assert [b["kind"] for b in saved["blocks"]] == ["search", "hero", "collection"]
    assert saved["blocks"][0]["reference_component"] == "SearchBar"
    assert saved["blocks"][2]["layout"] == "editorial"
