import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from modules.srs_generator.srs_document import build_srs, srs_markdown
from modules.srs_generator.srs_pdf import generate_srs_pdf

def sample():
    return {"name": "A&B <Shop>", "prompt": "Browse <products> & buy", "revision": 2,
            "requirements": [{"id": "REQ-001", "page": "products", "text": "Browse products", "approved": False}],
            "screen_configs": {"products": {"composition": {"blocks": [{"kind": "search"}, {"kind": "collection"}]}}},
            "nfr": [{"id": "NFR-001", "text": "Keyboard navigation"}]}

def test_shared_document_sections_and_actual_scope():
    doc = build_srs(sample())
    text = srs_markdown(sample())
    for section in doc["sections"]:
        assert section["title"] in text
    assert len(doc["sections"]) == 8
    assert "PlannedCommerce" in text
    assert "CartItem:" not in text
    assert "Pending review" in text
    assert "Keyboard navigation" in text
    assert "Technology Stack" in text
    assert "configured search, collection sections" in text


def test_srs_generators_use_project_scope():
    from modules.srs_generator.non_functional_requirement_generator import generate_non_functional_requirements
    from modules.srs_generator.technology_stack_identifier import identify_technology_stack

    simple = {"pages": ["home"], "features": ["catalog"]}
    stateful = {"pages": ["home", "cart", "profile"], "features": ["catalog", "cart"]}
    assert "AsyncStorage" not in identify_technology_stack(simple)
    assert "AsyncStorage" in identify_technology_stack(stateful)
    simple_categories = {item["category"] for item in generate_non_functional_requirements(simple)}
    stateful_categories = {item["category"] for item in generate_non_functional_requirements(stateful)}
    assert "Reliability" not in simple_categories
    assert {"Reliability", "Security & Privacy"} <= stateful_categories


def test_integrated_traceability_ids_and_engine_reframer():
    from modules.engine.reframer import reframe_input
    from modules.traceability_manager.id_assigner import IDAssigner

    assigner = IDAssigner()
    requirement = assigner.generate_id("", "REQ")
    component = assigner.generate_id(requirement, "CMP")
    assigner.register_link(requirement, component)
    assert requirement == "REQ-001"
    assert component == "REQ-001-CMP-001"
    assert assigner.get_dependencies(requirement) == [component]
    assert reframe_input("  Create a shop app  ")

def test_pdf_handles_user_markup_and_long_content():
    p = sample()
    p["prompt"] *= 300
    pdf = generate_srs_pdf(p)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000

def test_srs_routes_share_content(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from modules.engine import api
    monkeypatch.setattr(api, "fetch", lambda _: sample())
    app = FastAPI()
    app.include_router(api.router)
    client = TestClient(app)
    for suffix in ("srs.json", "srs.md", "srs.pdf"):
        response = client.get("/api/projects/example/" + suffix)
        assert response.status_code == 200
    assert client.get("/api/projects/example/srs.json").json() == build_srs(sample())
