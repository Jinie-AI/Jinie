import hashlib
import base64
import json
import secrets
import time
import os
import re
import httpx
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Header, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["auth"])

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
USERS_FILE = DATA_DIR / "users.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# In-memory token storage (token -> {user_id, expires_at})
TOKENS: dict[str, dict] = {}
PENDING_VERIFICATIONS: dict[str, dict] = {}
TOKEN_EXPIRY_SECONDS = 7 * 24 * 3600  # 7 days


def firebase_enabled():
    return bool(os.getenv("FIREBASE_WEB_API_KEY", "").strip())


# Firebase owns passwords and email verification; only verified identities receive workspace sessions.
def _firebase(action: str, payload: dict):
    key = os.getenv("FIREBASE_WEB_API_KEY", "").strip()
    try:
        response = httpx.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:{action}",
            params={"key": key}, json=payload, timeout=15,
        )
        data = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "Authentication service is unavailable. Please try again.") from None
    if not response.is_success:
        code = data.get("error", {}).get("message", "").split(" : ")[0]
        if action == "sendOobCode" and payload.get("requestType") == "PASSWORD_RESET" and code == "EMAIL_NOT_FOUND":
            return {}
        messages = {
            "EMAIL_EXISTS": "This email already has an account. Sign in instead.",
            "INVALID_EMAIL": "Enter a valid email address.",
            "OPERATION_NOT_ALLOWED": "Enable Email/Password in Firebase Authentication first.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
            "PASSWORD_LOGIN_DISABLED": "Email/password sign-in is disabled for this project.",
            "API_KEY_INVALID": "Check the Firebase configuration in backend/.env.",
        }
        raise HTTPException(400, messages.get(code, "Authentication failed. Check your email and password."))
    return data


def _firebase_login(req):
    return _firebase("signInWithPassword", {
        "email": req.email_or_username.strip(), "password": req.password,
        "returnSecureToken": True,
    })


def _firebase_account(id_token):
    users = _firebase("lookup", {"idToken": id_token}).get("users", [])
    if not users or not users[0].get("emailVerified") or users[0].get("disabled"):
        raise HTTPException(403, "Verify your email before signing in. Check your inbox and spam folder.")
    return users[0]


def _verification_ticket(identity):
    for ticket, pending in list(PENDING_VERIFICATIONS.items()):
        if pending["expires_at"] <= time.time():
            PENDING_VERIFICATIONS.pop(ticket, None)
    ticket = secrets.token_urlsafe(32)
    PENDING_VERIFICATIONS[ticket] = {
        "id_token": identity["idToken"],
        "expires_at": time.time() + min(int(identity.get("expiresIn", 3600)), 900),
    }
    return ticket


def _firebase_session(identity: dict, response: Response, request: Request = None):
    account = _firebase_account(identity["idToken"])
    user = _firebase_user(account)
    token = secrets.token_urlsafe(32)
    lifetime = min(int(identity.get("expiresIn", 3600)), 3600)
    # Read expiry only after Firebase has validated the token; this does not replace token validation.
    if identity["idToken"].count(".") == 2:
        try:
            payload = identity["idToken"].split(".")[1]
            claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            project_id = os.getenv("FIREBASE_PROJECT_ID", "jinie-web-app")
            if claims.get("aud") != project_id or claims.get("iss") != "https://securetoken.google.com/" + project_id or claims.get("sub") != account["localId"]:
                raise HTTPException(401, "Authentication token belongs to a different project or account.")
            lifetime = min(lifetime, int(claims["exp"]) - int(time.time()))
        except (KeyError, ValueError, TypeError):
            raise HTTPException(401, "Invalid authentication token.") from None
        if lifetime <= 0:
            raise HTTPException(401, "Authentication expired. Please sign in again.")
    TOKENS[token] = {"user": user, "id_token": identity["idToken"],
                     "expires_at": time.time() + lifetime, "checked_at": time.time(),
                     "asset_token": secrets.token_urlsafe(32)}
    response.headers["Cache-Control"] = "no-store"
    if request is not None:
        from modules.utilities import guest_sessions
        guest_sessions.claim(request.headers.get("x-jinie-guest", ""), user["id"])
    # Navigation and downloads use a separate capability that cannot change projects.
    return {"success": True, "token": token, "asset_token": TOKENS[token]["asset_token"],
            "user": _to_user_out(user)}


def _firebase_user(account):
    return {"id": account["localId"], "email": account["email"],
            "username": account["email"].split("@")[0],
            "full_name": account.get("displayName") or account["email"].split("@")[0],
            "email_verified": bool(account.get("emailVerified")),
            "photo_url": account.get("photoUrl", ""),
            "sign_in_methods": [item["providerId"] for item in account.get("providerUserInfo", []) if item.get("providerId")]}


def authorize_workspace(request: Request):
    if not firebase_enabled() or request.url.path == "/api/health" or request.url.path.startswith("/api/auth/"):
        return
    header = request.headers.get("authorization", "")
    token = header[7:] if header.startswith("Bearer ") else ""
    match = re.match(r"^/api/projects/([^/]+)(?:/(.*))?$", request.url.path)
    suffix = match.group(2) if match else ""
    if not token and request.method == "GET" and match and (
        (suffix or "").startswith("preview/") or suffix in {"download", "srs.pdf", "srs.json", "srs.md"}
    ):
        asset = request.query_params.get("asset_token", "")
        if (suffix or "").startswith("preview/~"):
            asset = suffix.split("/", 2)[1][1:]
        if asset:
            token = next((t for t, session in list(TOKENS.items())
                          if secrets.compare_digest(session.get("asset_token", ""), asset)), "")
    user = _get_user_from_token(token)
    if not user and not header:
        from modules.utilities import guest_sessions
        user = guest_sessions.identity(request.headers.get("x-jinie-guest", ""))
        if not user and request.method == "GET" and match and (
            (suffix or "").startswith("preview/") or suffix in {"download", "srs.pdf", "srs.json", "srs.md"}
        ):
            asset = request.query_params.get("asset_token", "")
            if (suffix or "").startswith("preview/~"):
                asset = suffix.split("/", 2)[1][1:]
            user = guest_sessions.identity(asset, asset=True)
    if not user:
        raise HTTPException(401, "Please sign in to your verified account.")
    request.state.user = user
    if match:
        from modules.utilities import store
        try:
            project = store.get(match.group(1))
        except KeyError:
            raise HTTPException(404, "Project not found") from None
        if project.get("owner_id") != user["id"]:
            raise HTTPException(404, "Project not found")


# Password protection: PBKDF2-HMAC-SHA256 with a random salt and 100,000 iterations; plaintext passwords are not stored.
def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return pwd_hash, salt


# Login verification: derives the supplied password hash and compares it using a constant-time comparison.
def _verify_password(password: str, salt: str, expected_hash: str) -> bool:
    pwd_hash, _ = _hash_password(password, salt)
    return secrets.compare_digest(pwd_hash, expected_hash)


def _load_users() -> list[dict]:
    if not USERS_FILE.exists():
        # Prepopulate with a demo developer account
        salt = secrets.token_hex(16)
        pwd_hash, _ = _hash_password("password123", salt)
        default_users = [
            {
                "id": "usr_demo",
                "username": "developer",
                "email": "dev@jinie.ai",
                "full_name": "Lead Developer",
                "password_hash": pwd_hash,
                "salt": salt,
                "created_at": time.time(),
            }
        ]
        USERS_FILE.write_text(json.dumps(default_users, indent=2), encoding="utf-8")
        return default_users
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_users(users: list[dict]):
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def _find_user_by_id(user_id: str) -> Optional[dict]:
    users = _load_users()
    for u in users:
        if u["id"] == user_id:
            return u
    return None


def _find_user_by_credential(credential: str) -> Optional[dict]:
    cred = credential.strip().lower()
    users = _load_users()
    for u in users:
        if u["email"].lower() == cred or u["username"].lower() == cred:
            return u
    return None


def _create_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    TOKENS[token] = {
        "user_id": user_id,
        "expires_at": time.time() + TOKEN_EXPIRY_SECONDS,
    }
    return token


def _get_user_from_token(token: str) -> Optional[dict]:
    if not token or token not in TOKENS:
        return None
    session = TOKENS[token]
    if time.time() > session["expires_at"]:
        del TOKENS[token]
        return None
    if firebase_enabled():
        if "id_token" not in session:
            return None
        if time.time() - session["checked_at"] > 30:
            try:
                account = _firebase_account(session["id_token"])
            except HTTPException as exc:
                if exc.status_code != 503:
                    TOKENS.pop(token, None)
                raise
            if account["localId"] != session["user"]["id"]:
                TOKENS.pop(token, None)
                return None
            session["checked_at"] = time.time()
            session["user"] = _firebase_user(account)
        return session["user"]
    return _find_user_by_id(session["user_id"])


# Schemas
class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email_or_username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    initials: str
    email_verified: bool = False
    photo_url: str = ""
    sign_in_methods: list[str] = Field(default_factory=list)


class AuthResponse(BaseModel):
    success: bool
    token: str
    user: UserOut


def _to_user_out(user: dict) -> UserOut:
    names = user["full_name"].strip().split()
    initials = (
        "".join([n[0].upper() for n in names[:2]]) or user["username"][:2].upper()
    )
    return UserOut(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        initials=initials,
        email_verified=user.get("email_verified", False),
        photo_url=_uploaded_photo_url(user["id"]) or user.get("photo_url", ""),
        sign_in_methods=user.get("sign_in_methods", ["password"]),
    )


@router.post("/signup")
def signup(req: SignupRequest):
    if firebase_enabled():
        if len(req.password) < 8:
            raise HTTPException(422, "Use a password with at least 8 characters.")
        identity = _firebase("signUp", {"email": req.email.strip(), "password": req.password,
                                        "returnSecureToken": True})
        _firebase("update", {"idToken": identity["idToken"], "displayName": req.full_name.strip()})
        try:
            _firebase("sendOobCode", {"requestType": "VERIFY_EMAIL", "idToken": identity["idToken"]})
        except HTTPException:
            raise HTTPException(503, "Account created, but the verification email could not be sent. Use Resend verification on Sign In.") from None
        return {"success": True, "verification_required": True,
                "verification_ticket": _verification_ticket(identity),
                "message": "Account created. Verify your email using the link in your inbox, then sign in."}
    users = _load_users()
    # Check if username or email already exists
    if any(u["username"].lower() == req.username.lower() for u in users):
        raise HTTPException(status_code=400, detail="Username is already taken")
    if any(u["email"].lower() == req.email.lower() for u in users):
        raise HTTPException(status_code=400, detail="Email is already registered")

    pwd_hash, salt = _hash_password(req.password)
    new_user = {
        "id": f"usr_{secrets.token_hex(6)}",
        "username": req.username,
        "email": req.email,
        "full_name": req.full_name,
        "password_hash": pwd_hash,
        "salt": salt,
        "created_at": time.time(),
    }
    users.append(new_user)
    _save_users(users)

    token = _create_token(new_user["id"])
    return AuthResponse(success=True, token=token, user=_to_user_out(new_user))


@router.post("/login")
def login(req: LoginRequest, response: Response, request: Request = None):
    if firebase_enabled():
        return _firebase_session(_firebase_login(req), response, request)
    user = _find_user_by_credential(req.email_or_username)
    if not user or not _verify_password(
        req.password, user["salt"], user["password_hash"]
    ):
        raise HTTPException(
            status_code=401, detail="Invalid username/email or password"
        )

    token = _create_token(user["id"])
    return AuthResponse(success=True, token=token, user=_to_user_out(user))


class EmailRequest(BaseModel):
    email: str = Field(min_length=5, max_length=120)


@router.post("/reset-password")
def reset_password(req: EmailRequest):
    if not firebase_enabled():
        raise HTTPException(503, "Firebase authentication is not configured.")
    _firebase("sendOobCode", {"requestType": "PASSWORD_RESET", "email": req.email.strip()})
    return {"success": True, "message": "If this email has an account, a password reset link has been sent."}


@router.post("/resend-verification")
def resend_verification(req: LoginRequest):
    if not firebase_enabled():
        raise HTTPException(503, "Firebase authentication is not configured.")
    identity = _firebase_login(req)
    _firebase("sendOobCode", {"requestType": "VERIFY_EMAIL", "idToken": identity["idToken"]})
    return {"success": True, "message": "Verification Link sent",
            "verification_ticket": _verification_ticket(identity)}


class VerificationRequest(BaseModel):
    ticket: str = Field(min_length=20, max_length=128)


@router.post("/verification-status")
def verification_status(req: VerificationRequest, response: Response, request: Request = None):
    response.headers["Cache-Control"] = "no-store"
    pending = PENDING_VERIFICATIONS.get(req.ticket)
    if not firebase_enabled() or not pending or pending["expires_at"] <= time.time():
        PENDING_VERIFICATIONS.pop(req.ticket, None)
        raise HTTPException(401, "Verification check expired. Sign in or resend verification.")
    users = _firebase("lookup", {"idToken": pending["id_token"]}).get("users", [])
    if not users or users[0].get("disabled"):
        PENDING_VERIFICATIONS.pop(req.ticket, None)
        raise HTTPException(403, "This account is unavailable.")
    if not users[0].get("emailVerified"):
        return {"success": True, "verified": False}
    session = _firebase_session({"idToken": pending["id_token"], "expiresIn": 3600}, response, request)
    PENDING_VERIFICATIONS.pop(req.ticket, None)
    return {**session, "verified": True, "message": "Verified Successfully"}


class FirebaseLoginRequest(BaseModel):
    id_token: str = Field(min_length=20, max_length=10000)


@router.post("/firebase")
def firebase_login(req: FirebaseLoginRequest, response: Response, request: Request = None):
    if not firebase_enabled():
        raise HTTPException(503, "Firebase authentication is not configured.")
    # Firebase validates the ID token via account lookup before Jinie creates its own workspace session.
    return _firebase_session({"idToken": req.id_token, "expiresIn": 3600}, response, request)


@router.post("/guest")
def start_guest(request: Request, response: Response):
    from modules.utilities import guest_sessions
    response.headers["Cache-Control"] = "no-store"
    return guest_sessions.start(request.headers.get("x-jinie-guest", ""))


def prompt_budget(request: Request):
    user = getattr(request.state, "user", {})
    if not user.get("is_guest"):
        yield
        return
    from modules.utilities import guest_sessions
    guest_sessions.reserve(user)
    try:
        yield
    except BaseException:
        guest_sessions.refund(user)
        raise


@router.get("/me")
def get_me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authentication token"
        )
    token = authorization[7:].strip()
    user = _get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=401, detail="Session expired or invalid. Please sign in again."
        )
    return {"success": True, "user": _to_user_out(user)}


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        TOKENS.pop(token, None)
    return {"success": True, "message": "Logged out successfully"}


class ProfileRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=2048)


@router.put("/profile")
def update_profile(req: ProfileRequest, authorization: Optional[str] = Header(None)):
    token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else ""
    user = _get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Please sign in again.")
    full_name = req.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(422, "Enter a name with at least two characters.")
    photo_url = req.photo_url.strip() if req.photo_url is not None else None
    if photo_url:
        from urllib.parse import urlparse
        parsed = urlparse(photo_url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise HTTPException(422, "Use an HTTPS image URL without embedded credentials.")
    if firebase_enabled():
        session = TOKENS[token]
        payload = {"idToken": session["id_token"], "displayName": full_name}
        if photo_url:
            payload["photoUrl"] = photo_url
        elif photo_url is not None:
            payload["deleteAttribute"] = ["PHOTO_URL"]
        _firebase("update", payload)
        account = _firebase_account(session["id_token"])
        session["user"] = _firebase_user(account)
        session["checked_at"] = time.time()
        user = session["user"]
    else:
        users = _load_users()
        for item in users:
            if item["id"] == user["id"]:
                item.update(full_name=full_name)
                if photo_url is not None:
                    item["photo_url"] = photo_url
                user = item
                break
        _save_users(users)
    return {"success": True, "user": _to_user_out(user)}


def _avatar_path(user_id):
    from modules.utilities import store
    return store.DATA / "avatars" / (hashlib.sha256(user_id.encode()).hexdigest() + ".jpg")


def _uploaded_photo_url(user_id):
    path = _avatar_path(user_id)
    return "/api/auth/avatars/" + path.name + "?v=" + str(path.stat().st_mtime_ns) if path.is_file() else ""


@router.post("/profile/photo")
async def upload_profile_photo(file: UploadFile = File(...), authorization: Optional[str] = Header(None)):
    token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else ""
    user = _get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Please sign in again.")
    # Decode and re-encode uploads so executable content and original image metadata are not stored.
    import io
    import warnings
    from PIL import Image, ImageOps, UnidentifiedImageError
    raw = await file.read(5 * 1024 * 1024 + 1)
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(413, "Choose an image smaller than 5 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as image:
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise HTTPException(422, "Choose a JPG, PNG or WebP image.")
                if image.width * image.height > 20_000_000:
                    raise HTTPException(422, "Choose an image below 20 megapixels.")
                image.load()
                avatar = ImageOps.fit(ImageOps.exif_transpose(image).convert("RGB"), (256, 256))
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(422, "This image could not be read. Choose a valid JPG, PNG or WebP.") from None
    path = _avatar_path(user["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + "." + secrets.token_hex(8) + ".tmp")
    avatar.save(temporary, format="JPEG", quality=88)
    temporary.replace(path)
    return {"success": True, "user": _to_user_out(user)}


@router.get("/avatars/{filename}")
def avatar_image(filename: str):
    if not re.fullmatch(r"[0-9a-f]{64}\.jpg", filename):
        raise HTTPException(404, "Photo not found")
    from modules.utilities import store
    path = store.DATA / "avatars" / filename
    if not path.is_file():
        raise HTTPException(404, "Photo not found")
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"})
