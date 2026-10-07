import sys
import time
from pathlib import Path

import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from modules.utilities import auth, store


@pytest.fixture(autouse=True)
def firebase_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("FIREBASE_WEB_API_KEY", "test-key")
    monkeypatch.setattr(auth, "TOKENS", {})
    monkeypatch.setattr(auth, "PENDING_VERIFICATIONS", {})
    monkeypatch.setattr(store, "DATA", tmp_path)


def identity(verified=True):
    return {"localId": "alice", "email": "alice@example.com", "emailVerified": verified,
            "displayName": "Alice Test"}


def make_session(monkeypatch):
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity()]})
    return auth._firebase_session({"idToken": "firebase-token", "expiresIn": "3600"}, Response())


def request(path, token="", method="GET", query=""):
    return Request({"type": "http", "method": method, "path": path,
                    "query_string": query.encode(),
                    "headers": [(b"authorization", ("Bearer " + token).encode())] if token else []})


def test_unverified_account_cannot_get_session(monkeypatch):
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity(False)]})
    with pytest.raises(HTTPException) as exc:
        auth._firebase_session({"idToken": "test"}, Response())
    assert exc.value.status_code == 403
    assert not auth.TOKENS


def test_signup_sends_email_without_workspace_token(monkeypatch):
    calls = []
    def firebase(action, payload):
        calls.append((action, payload))
        return {"idToken": "firebase-token"}
    monkeypatch.setattr(auth, "_firebase", firebase)
    result = auth.signup(auth.SignupRequest(full_name="Alice Test", username="alice", email="alice@example.com", password="safe-password"))
    assert result["verification_required"] is True
    assert "token" not in result and not auth.TOKENS
    assert [call[0] for call in calls] == ["signUp", "update", "sendOobCode"]
    assert calls[-1][1]["requestType"] == "VERIFY_EMAIL"


def test_sessions_expire_and_are_rechecked(monkeypatch):
    session = make_session(monkeypatch)
    token = session["token"]
    assert auth._get_user_from_token(token)["id"] == "alice"
    auth.TOKENS[token]["checked_at"] = 0
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity(False)]})
    with pytest.raises(HTTPException):
        auth._get_user_from_token(token)
    assert token not in auth.TOKENS


def test_anonymous_and_cross_user_project_access_denied(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        auth.authorize_workspace(request("/api/projects"))
    assert exc.value.status_code == 401
    session = make_session(monkeypatch)
    monkeypatch.setattr(store, "get", lambda pid: {"owner_id": "bob"})
    with pytest.raises(HTTPException) as exc:
        auth.authorize_workspace(request("/api/projects/project-1", session["token"]))
    assert exc.value.status_code == 404


def test_preview_capability_cannot_modify_project(monkeypatch):
    session = make_session(monkeypatch)
    monkeypatch.setattr(store, "get", lambda pid: {"owner_id": "alice"})
    preview = request(f"/api/projects/project-1/preview/~{session['asset_token']}/app.js")
    auth.authorize_workspace(preview)
    assert preview.state.user["id"] == "alice"
    with pytest.raises(HTTPException) as exc:
        auth.authorize_workspace(request("/api/projects/project-1/build", method="POST", query="asset_token=" + session["asset_token"]))
    assert exc.value.status_code == 401


def test_old_local_tokens_cannot_bypass_firebase():
    auth.TOKENS["old"] = {"user_id": "usr_demo", "expires_at": time.time() + 100}
    assert auth._get_user_from_token("old") is None


def test_http_routes_require_identity_and_hide_other_projects(monkeypatch):
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    app = FastAPI()
    @app.get("/api/projects/{pid}", dependencies=[Depends(auth.authorize_workspace)])
    def project(pid: str, request: Request):
        return {"id": pid, "owner": request.state.user["id"]}
    client = TestClient(app)
    assert client.get("/api/projects/example").status_code == 401
    session = make_session(monkeypatch)
    monkeypatch.setattr(store, "get", lambda pid: {"owner_id": "alice"})
    headers = {"Authorization": "Bearer " + session["token"]}
    assert client.get("/api/projects/example", headers=headers).json()["owner"] == "alice"
    monkeypatch.setattr(store, "get", lambda pid: {"owner_id": "bob"})
    assert client.get("/api/projects/example", headers=headers).status_code == 404


def test_verification_polls_real_status_and_exchanges_ticket_once(monkeypatch):
    ticket = auth._verification_ticket({"idToken": "firebase-token"})
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity(False)]})
    req = auth.VerificationRequest(ticket=ticket)
    assert auth.verification_status(req, Response())["verified"] is False
    assert not auth.TOKENS
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity()]})
    result = auth.verification_status(req, Response())
    assert result["verified"] and result["message"] == "Verified Successfully"
    assert result["user"].id == "alice"
    assert ticket not in auth.PENDING_VERIFICATIONS
    with pytest.raises(HTTPException):
        auth.verification_status(req, Response())


def test_google_exchange_rejects_unverified_identity(monkeypatch):
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity(False)]})
    with pytest.raises(HTTPException) as exc:
        auth.firebase_login(auth.FirebaseLoginRequest(id_token="x" * 30), Response())
    assert exc.value.status_code == 403
    assert not auth.TOKENS


def test_expired_verification_ticket_does_not_contact_firebase(monkeypatch):
    ticket = auth._verification_ticket({"idToken": "test"})
    auth.PENDING_VERIFICATIONS[ticket]["expires_at"] = 0
    monkeypatch.setattr(auth, "_firebase", lambda *args: pytest.fail("Expired ticket must not be used"))
    with pytest.raises(HTTPException) as exc:
        auth.verification_status(auth.VerificationRequest(ticket=ticket), Response())
    assert exc.value.status_code == 401


def test_other_firebase_project_cannot_impersonate_owner(monkeypatch):
    import base64
    import json
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "jinie-web-app")
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity()]})
    claims = {"aud": "another-project", "iss": "https://securetoken.google.com/another-project", "sub": "alice", "exp": int(time.time()) + 3600}
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    with pytest.raises(HTTPException) as exc:
        auth.firebase_login(auth.FirebaseLoginRequest(id_token="header." + payload + ".signature"), Response())
    assert exc.value.status_code == 401
    assert not auth.TOKENS


def test_profile_update_requires_session_and_rejects_unsafe_photo(monkeypatch):
    req = auth.ProfileRequest(full_name="Alice Updated")
    with pytest.raises(HTTPException) as exc:
        auth.update_profile(req, None)
    assert exc.value.status_code == 401
    session = make_session(monkeypatch)
    req = auth.ProfileRequest(full_name="Alice Updated", photo_url="javascript:alert(1)")
    with pytest.raises(HTTPException) as exc:
        auth.update_profile(req, "Bearer " + session["token"])
    assert exc.value.status_code == 422


def test_profile_saved_to_firebase_without_changing_identity(monkeypatch):
    session = make_session(monkeypatch)
    account = {**identity(), "photoUrl": "https://example.com/photo.jpg",
               "providerUserInfo": [{"providerId": "google.com"}]}
    calls = []
    def firebase(action, payload):
        calls.append((action, payload))
        if action == "update":
            account["displayName"] = payload["displayName"]
            return {}
        return {"users": [account]}
    monkeypatch.setattr(auth, "_firebase", firebase)
    result = auth.update_profile(auth.ProfileRequest(full_name="Alice Updated", photo_url="https://example.com/photo.jpg"), "Bearer " + session["token"])
    assert result["user"].id == "alice"
    assert result["user"].full_name == "Alice Updated"
    assert result["user"].sign_in_methods == ["google.com"]
    assert result["user"].email_verified is True
    assert calls[0][0] == "update"
    assert auth.TOKENS[session["token"]]["user"]["full_name"] == "Alice Updated"


def test_clearing_photo_uses_firebase_delete_attribute(monkeypatch):
    session = make_session(monkeypatch)
    calls = []
    def firebase(action, payload):
        calls.append((action, payload))
        return {"users": [identity()]}
    monkeypatch.setattr(auth, "_firebase", firebase)
    result = auth.update_profile(auth.ProfileRequest(full_name="Alice Updated", photo_url=""), "Bearer " + session["token"])
    assert calls[0][1]["deleteAttribute"] == ["PHOTO_URL"]
    assert result["user"].photo_url == ""


def test_photo_upload_is_saved_resized_and_available_after_login(monkeypatch):
    import asyncio
    import io
    from PIL import Image
    from starlette.datastructures import UploadFile
    session = make_session(monkeypatch)
    image = io.BytesIO()
    Image.new("RGB", (600, 400), "purple").save(image, format="PNG")
    result = asyncio.run(auth.upload_profile_photo(UploadFile(io.BytesIO(image.getvalue()), filename="photo.png"), "Bearer " + session["token"]))
    path = auth._avatar_path("alice")
    with Image.open(path) as saved:
        assert saved.size == (256, 256) and saved.format == "JPEG"
    assert result["user"].photo_url.startswith("/api/auth/avatars/")
    assert auth._to_user_out(auth._firebase_user(identity())).photo_url == result["user"].photo_url


def test_invalid_photo_and_missing_auth_are_rejected(monkeypatch):
    import asyncio
    import io
    from starlette.datastructures import UploadFile
    session = make_session(monkeypatch)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.upload_profile_photo(UploadFile(io.BytesIO(b"<script>bad</script>"), filename="image.jpg"), "Bearer " + session["token"]))
    assert exc.value.status_code == 422
    assert not auth._avatar_path("alice").exists()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(auth.upload_profile_photo(UploadFile(io.BytesIO(b"test"), filename="photo.png"), None))
    assert exc.value.status_code == 401


def test_guest_gets_two_prompts_and_refresh_does_not_reset_budget(monkeypatch):
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from modules.utilities import guest_sessions
    app = FastAPI()
    app.include_router(auth.router, prefix="/api")
    @app.post("/api/projects", dependencies=[Depends(auth.authorize_workspace), Depends(auth.prompt_budget)])
    def create(request: Request):
        return {"owner_id": request.state.user["id"]}
    client = TestClient(app)
    guest = client.post("/api/auth/guest").json()
    headers = {"X-Jinie-Guest": guest["guest_token"]}
    assert client.post("/api/projects", headers=headers).status_code == 200
    assert client.post("/api/projects", headers=headers).status_code == 200
    result = client.post("/api/projects", headers=headers)
    assert result.status_code == 403 and "2 free prompts" in result.json()["detail"]
    assert client.post("/api/auth/guest", headers=headers).json()["remaining"] == 0
    assert guest_sessions.identity(guest["guest_token"])["used"] == 2


def test_failed_guest_generation_refunds_allowance(monkeypatch):
    from modules.utilities import guest_sessions
    guest = guest_sessions.start()
    req = request("/api/projects", method="POST")
    req.state.user = guest_sessions.identity(guest["guest_token"])
    budget = auth.prompt_budget(req)
    next(budget)
    with pytest.raises(ValueError):
        budget.throw(ValueError("Generation failed"))
    assert guest_sessions.start(guest["guest_token"])["remaining"] == 2


def test_guest_projects_are_private_and_claimed_by_verified_login(monkeypatch):
    from modules.utilities import guest_sessions
    guest = guest_sessions.start()
    guest_user = guest_sessions.identity(guest["guest_token"])
    projects = {"id": "example", "owner_id": guest_user["id"]}
    monkeypatch.setattr(store, "get", lambda pid: projects)
    monkeypatch.setattr(store, "listing", lambda: [projects])
    monkeypatch.setattr(store, "save", lambda project: None)
    req = Request({"type": "http", "method": "GET", "path": "/api/projects/example", "query_string": b"", "headers": [(b"x-jinie-guest", guest["guest_token"].encode())]})
    auth.authorize_workspace(req)
    assert req.state.user["id"] == projects["owner_id"]
    other = guest_sessions.start()
    req2 = Request({"type": "http", "method": "GET", "path": "/api/projects/example", "query_string": b"", "headers": [(b"x-jinie-guest", other["guest_token"].encode())]})
    with pytest.raises(HTTPException) as exc:
        auth.authorize_workspace(req2)
    assert exc.value.status_code == 404
    monkeypatch.setattr(auth, "_firebase", lambda action, payload: {"users": [identity()]})
    auth._firebase_session({"idToken": "firebase-token", "expiresIn": 3600}, Response(), req)
    assert projects["owner_id"] == "alice"
