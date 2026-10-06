import io
import json
import sys
import time
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_project_runtime(monkeypatch, tmp_path):
    from modules.engine import api
    from modules.compiler import compiler
    from modules.utilities import store
    from modules.engine.domain import extract

    monkeypatch.setattr(store, "DATA", tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(api.models, "intake", extract)
    monkeypatch.setattr(
        api.models,
        "recommend",
        lambda *args: [{"id": "grid", "source": "test", "score": None}],
    )
    monkeypatch.setattr(compiler, "code_candidate", lambda _: None)


def new():
    r = client.post(
        "/api/projects",
        json={
            "name": "Test shop",
            "prompt": "Build a clothing store with cart checkout search about and contact",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_custom_record_build_and_export():
    response = client.post("/api/projects", json={"name": "Skin care", "prompt": "Makeup app with homescreen, menu screen, user profile, dont add settings. Include a medical record with patient name, patient id, patient condition, skin colour."})
    assert response.status_code == 201, response.text
    p = response.json()
    assert "settings" not in p["spec"]["pages"]
    assert "custom_medical_record" in p["screen_configs"]
    p = approve(p)
    assert client.post(f"/api/projects/{p['id']}/build").status_code == 200
    built = wait(p["id"])
    assert built["status"] == "ready", built.get("error")
    archive = zipfile.ZipFile(io.BytesIO(client.get(f"/api/projects/{p['id']}/download").content))
    config_path = next(n for n in archive.namelist() if n.endswith("src/config.json"))
    config = json.loads(archive.read(config_path))
    assert config["screen_configs"]["custom_medical_record"]["sections"][0]["fields"][0]["label"] == "Patient name"


def test_domain_catalog_screen_keeps_clickable_product_flow():
    response = client.post(
        "/api/projects",
        json={
            "name": "Clothes",
            "prompt": "Create a clothing store with home screen and clothes screen.",
        },
    )
    assert response.status_code == 201, response.text
    project = response.json()
    assert {"home", "products", "detail"} <= set(project["spec"]["pages"])
    assert "custom_clothes" not in project["spec"]["pages"]
    assert any(item["page"] == "products" for item in project["requirements"])


def approve(p):
    for r in p["requirements"]:
        r["approved"] = True
    res = client.put(
        f"/api/projects/{p['id']}/review",
        json={k: p[k] for k in ["requirements", "design"]}
        | {"business": p["spec"]["business"]},
    )
    assert res.status_code == 200, res.text
    return res.json()


def wait(pid):
    for _ in range(300):
        p = client.get("/api/projects/" + pid).json()
        if p["status"] != "building":
            return p
        time.sleep(0.1)
    pytest.fail("build timed out")


def test_complete_pipeline_and_edit():
    p = new()
    url = "/api/projects/" + p["id"]
    assert client.post(url + "/build").status_code == 409
    p = approve(p)
    assert client.post(url + "/build").status_code == 200
    p = wait(p["id"])
    assert p["status"] == "ready", p.get("error")
    assert len(p["traceability"]) == 8
    assert all("src/components/AppView.jsx" in t["files"] for t in p["traceability"])
    assert any(t["id"] == "FILES-001" and t["status"] == "passed" for t in p["tests"])
    assert client.get(url + "/preview/index.html").status_code == 200
    archive = client.get(url + "/download")
    assert archive.status_code == 200
    with zipfile.ZipFile(io.BytesIO(archive.content)) as z:
        assert "Test shop-jinie/App.jsx" in z.namelist()
        package = json.loads(z.read("Test shop-jinie/package.json"))
        assert package["dependencies"]["react-native"] == "0.81.5"
    original = client.get(url + "/file", params={"path": "src/config.json"}).json()[
        "content"
    ]
    config = json.loads(original)
    config["name"] = "Edited shop"
    assert (
        client.put(
            url + "/file",
            params={"path": "src/config.json"},
            json={"content": json.dumps(config)},
        ).status_code
        == 200
    )
    saved = client.get(url).json()
    assert set(saved["edits"][-1]["affected_requirements"]) == {r["id"] for r in saved["requirements"]}
    assert client.get(url + "/download").status_code == 409
    assert client.post(url + "/rebuild").status_code == 200
    p = wait(p["id"])
    assert p["status"] == "ready", p.get("error")
    # A failed edited build must not replace the last successful preview.
    previous_bundle = client.get(url + "/preview/app.js").content
    app_source = client.get(url + "/file", params={"path": "App.jsx"}).json()["content"]
    client.put(
        url + "/file",
        params={"path": "App.jsx"},
        json={"content": "export default function Broken( {"},
    )
    assert client.post(url + "/rebuild").status_code == 200
    failed = wait(p["id"])
    assert failed["status"] == "failed"
    assert client.get(url + "/preview/app.js").content == previous_bundle
    assert client.get(url + "/download").status_code == 409
    client.put(url + "/file", params={"path": "App.jsx"}, json={"content": app_source})
    client.post(url + "/rebuild")
    assert wait(p["id"])["status"] == "ready"
    r = client.post(
        url + "/feedback",
        json={
            "requirement_id": "REQ-001",
            "text": "Change the home styling",
            "rating": 4,
        },
    )
    assert r.status_code == 200 and not r.json()["requirements"][0]["approved"]
    assert client.post(url + "/build").status_code == 409


def test_validation_and_paths():
    assert client.post("/api/projects", json={"prompt": "        "}).status_code == 422
    p = new()
    url = "/api/projects/" + p["id"]
    for path in ["../../main.py", "/etc/passwd"]:
        assert client.get(url + "/file", params={"path": path}).status_code == 400
    assert (
        client.post(
            url + "/feedback",
            json={"requirement_id": "BAD", "text": "hello", "rating": 1},
        ).status_code
        == 422
    )
    assert client.post(url + "/deploy").status_code == 409
    assert (
        client.post(
            "/api/references",
            files={"file": ("a.exe", b"fake", "application/octet-stream")},
        ).status_code
        == 415
    )
    assert (
        client.post(
            "/api/references",
            files={"file": ("a.txt", b"clothing business", "text/plain")},
        ).json()["text"]
        == "clothing business"
    )
    duplicate = [p["requirements"][0], p["requirements"][0]]
    assert (
        client.put(
            url + "/review",
            json={
                "requirements": duplicate,
                "design": p["design"],
                "business": "clothing",
            },
        ).status_code
        == 422
    )


def test_dataset_split_groups():
    for file in ["intake", "layouts", "code"]:
        rows = [
            json.loads(x)
            for x in (ROOT / "training/data" / f"{file}.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        groups = {
            s: {r["group_id"] for r in rows if r["split"] == s}
            for s in ["train", "validation", "test"]
        }
        assert not groups["train"] & groups["test"]
        assert not groups["train"] & groups["validation"]
        assert not groups["test"] & groups["validation"]


def test_export_preserves_reviewed_components(monkeypatch):
    from modules.compiler import compiler
    from modules.utilities import store
    p = approve(new())
    reviewed = (compiler.TEMPLATES / "ProductCard.jsx").read_text(encoding="utf-8")
    candidate = reviewed.replace('borderRadius: 16', 'borderRadius: 0')
    monkeypatch.setattr(compiler, "code_candidate", lambda _: candidate)
    compiler.compile_project(p)
    generated = store.folder(p["id"]) / "source"
    assert (generated / "src/components/ProductCard.jsx").read_text(encoding="utf-8") == reviewed
    assert (generated / "src/components/AppView.jsx").read_text(encoding="utf-8") == (compiler.TEMPLATES / "AppView.jsx").read_text(encoding="utf-8")
    config = json.loads((generated / "src/config.json").read_text(encoding="utf-8"))
    assert config["products"] == p["spec"]["products"]
    assert config["screen_configs"] == p["screen_configs"]
