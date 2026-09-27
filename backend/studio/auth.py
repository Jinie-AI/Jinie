import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["auth"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# In-memory token storage (token -> {user_id, expires_at})
TOKENS: dict[str, dict] = {}
TOKEN_EXPIRY_SECONDS = 7 * 24 * 3600  # 7 days


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return pwd_hash, salt


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
    )


@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest):
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


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    user = _find_user_by_credential(req.email_or_username)
    if not user or not _verify_password(
        req.password, user["salt"], user["password_hash"]
    ):
        raise HTTPException(
            status_code=401, detail="Invalid username/email or password"
        )

    token = _create_token(user["id"])
    return AuthResponse(success=True, token=token, user=_to_user_out(user))


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
