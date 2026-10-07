"""Persistent guest ownership and two-prompt allowance per browser session."""
import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from fastapi import HTTPException
from modules.utilities import store


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


@contextmanager
def database():
    with sqlite3.connect(store.DATA / "guest_sessions.sqlite3", timeout=30) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS guests (token TEXT PRIMARY KEY, asset TEXT UNIQUE, used INTEGER NOT NULL DEFAULT 0)")
        yield connection


def identity(token, asset=False):
    if not token:
        return None
    with database() as connection:
        row = connection.execute("SELECT token, used FROM guests WHERE " + ("asset" if asset else "token") + "=?", (digest(token),)).fetchone()
    return {"id": "guest:" + row[0], "is_guest": True, "used": row[1]} if row else None


def start(token=""):
    existing = identity(token)
    if not existing:
        token = secrets.token_urlsafe(32)
        asset = digest("jinie-preview:" + token)
        with database() as connection:
            connection.execute("INSERT INTO guests(token,asset) VALUES(?,?)", (digest(token), digest(asset)))
        existing = identity(token)
    return {"guest_token": token, "asset_token": digest("jinie-preview:" + token),
            "used": existing["used"], "remaining": max(0, 2 - existing["used"])}


def reserve(user):
    with database() as connection:
        result = connection.execute("UPDATE guests SET used=used+1 WHERE token=? AND used<2", (user["id"][6:],))
    if result.rowcount != 1:
        raise HTTPException(403, "You’ve used your 2 free prompts. Log in or create an account to continue.")


def refund(user):
    with database() as connection:
        connection.execute("UPDATE guests SET used=MAX(0,used-1) WHERE token=?", (user["id"][6:],))


def claim(token, user_id):
    guest = identity(token)
    if not guest:
        return
    with store.LOCK:
        for project in store.listing():
            if project.get("owner_id") == guest["id"]:
                project["owner_id"] = user_id
                store.save(project)
