import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from fastapi.testclient import TestClient
from main import app
from studio import mobile_deploy as mobile
from studio import store

client = TestClient(app)
PID = "a" * 32
SETTINGS = {
    "expo_project_id": "11111111-1111-4111-8111-111111111111",
    "owner": "demo",
    "slug": "demo-shop",
    "android_package": "com.demo.shop",
    "ios_bundle": "com.demo.shop",
    "asc_app_id": "12345678",
    "credentials_ready": True,
}


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DATA", tmp_path)
    monkeypatch.setattr(mobile.shutil, "which", lambda _: "eas")
    monkeypatch.setenv("EXPO_TOKEN", "test-secret-not-real")
    monkeypatch.delenv("JINIE_GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    store.save(
        {
            "id": PID,
            "revision": 2,
            "build_revision": 2,
            "status": "ready",
            "mobile_settings": SETTINGS,
        }
    )
    store.write(PID, "app.json", json.dumps({"expo": {"name": "Demo"}}))


def test_preflight_missing_setup_and_stale_build(monkeypatch):
    p = store.get(PID)
    p.pop("mobile_settings")
    p["build_revision"] = 1
    monkeypatch.delenv("EXPO_TOKEN")
    issues = mobile.preflight(p, "all")
    assert len(issues) == 3
    assert (
        client.post(
            f"/api/projects/{PID}/mobile-deployment", json={"platform": "wrong"}
        ).status_code
        == 422
    )


def test_duplicate_job_is_blocked(monkeypatch):
    monkeypatch.setattr(
        mobile.threading, "Thread", lambda **kw: SimpleNamespace(start=lambda: None)
    )
    url = f"/api/projects/{PID}/mobile-deployment"
    assert client.post(url, json={"platform": "android"}).status_code == 202
    assert client.post(url, json={"platform": "android"}).status_code == 409
    assert client.put(url + "/settings", json=SETTINGS).status_code == 409


def prepare():
    p = store.get(PID)
    p.update(
        status="deploying",
        mobile_deployment={"id": "job", "state": "queued", "builds": []},
    )
    store.save(p)


def test_success_runs_signed_build_then_submission(monkeypatch):
    prepare()
    calls = []

    def run(args, cwd):
        calls.append(args)
        if args[0] == "build":
            return json.dumps(
                [
                    {
                        "id": "22222222-2222-4222-8222-222222222222",
                        "platform": "ANDROID",
                        "status": "FINISHED",
                    }
                ]
            )
        return "Uploaded"

    monkeypatch.setattr(mobile, "run_eas", run)
    mobile.work(PID, "job", "android")
    p = store.get(PID)
    assert p["mobile_deployment"]["state"] == "submitted"
    assert p["status"] == "ready"
    assert [c[0] for c in calls] == ["build", "submit"]
    assert "--non-interactive" in calls[0]
    target = store.folder(PID) / "mobile-jobs/job"
    config = json.loads((target / "app.json").read_text())
    assert config["expo"]["android"]["package"] == "com.demo.shop"
    assert (
        json.loads((target / "eas.json").read_text())["submit"]["production"][
            "android"
        ]["track"]
        == "internal"
    )
    assert "test-secret" not in json.dumps(p)


def test_failed_or_missing_platform_never_claims_submitted(monkeypatch):
    prepare()
    monkeypatch.setattr(
        mobile,
        "run_eas",
        lambda *_: json.dumps([{"platform": "ANDROID", "status": "ERRORED"}]),
    )
    mobile.work(PID, "job", "all")
    assert store.get(PID)["mobile_deployment"]["state"] == "failed"


def test_submission_failure_preserves_build_link(monkeypatch):
    prepare()

    def run(args, cwd):
        if args[0] == "submit":
            raise RuntimeError("Store rejected the upload")
        return json.dumps(
            [
                {
                    "id": "22222222-2222-4222-8222-222222222222",
                    "platform": "IOS",
                    "status": "FINISHED",
                }
            ]
        )

    monkeypatch.setattr(mobile, "run_eas", run)
    mobile.work(PID, "job", "ios")
    job = store.get(PID)["mobile_deployment"]
    assert job["state"] == "failed" and len(job["builds"]) == 1
