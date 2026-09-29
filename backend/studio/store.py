import json
import os
import sqlite3
import threading
from pathlib import Path

from .domain import ROOT

DATA = Path(os.getenv("JINIE_DATA_DIR", str(ROOT / "runtime")))
DATA.mkdir(parents=True, exist_ok=True)
LOCK = threading.RLock()
_MONGO_CLIENT = None


def mongo_collection():
    """Reuse a connection pool; never silently switch databases on failure."""
    global _MONGO_CLIENT
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        return None
    with LOCK:
        if _MONGO_CLIENT is None:
            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=5000,
                                 connectTimeoutMS=5000, socketTimeoutMS=15000)
            try:
                client.admin.command("ping")
            except Exception:
                client.close()
                raise RuntimeError("MongoDB connection failed. Check backend/.env, database credentials and Atlas network access.") from None
            _MONGO_CLIENT = client
    return _MONGO_CLIENT[os.getenv("MONGODB_DATABASE", "jinie")]["projects"]


def close():
    global _MONGO_CLIENT
    if _MONGO_CLIENT is not None:
        _MONGO_CLIENT.close()
        _MONGO_CLIENT = None


def migrate_sqlite():
    """Copy local projects without replacing records already in MongoDB."""
    collection = mongo_collection()
    if collection is None:
        raise RuntimeError("Set MONGODB_URI in backend/.env first.")
    with connection() as con:
        rows = con.execute("SELECT data FROM projects ORDER BY rowid").fetchall()
    count = 0
    for row in rows:
        project = json.loads(row[0])
        result = collection.update_one(
            {"_id": project["id"]}, {"$setOnInsert": {"project": project}}, upsert=True
        )
        count += result.upserted_id is not None
    return count



def connection():
    con = sqlite3.connect(DATA / "projects.sqlite3", timeout=30)
    con.execute(
        "CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, data TEXT NOT NULL)"
    )
    return con


def save(project):
    collection = mongo_collection()
    if collection is not None:
        collection.replace_one({"_id": project["id"]},
                               {"_id": project["id"], "project": project}, upsert=True)
        return
    with LOCK, connection() as con:
        con.execute(
            "INSERT OR REPLACE INTO projects VALUES(?,?)",
            (project["id"], json.dumps(project, ensure_ascii=False)),
        )


def get(pid):
    collection = mongo_collection()
    if collection is not None:
        record = collection.find_one({"_id": pid})
        if record is None:
            raise KeyError(pid)
        return record["project"]
    with connection() as con:
        row = con.execute("SELECT data FROM projects WHERE id=?", (pid,)).fetchone()
    if not row:
        raise KeyError(pid)
    return json.loads(row[0])


def listing():
    collection = mongo_collection()
    if collection is not None:
        return [record["project"] for record in
                collection.find({}).sort([("project.created_at", -1), ("_id", -1)])]
    with connection() as con:
        rows = con.execute("SELECT data FROM projects ORDER BY rowid DESC").fetchall()
    return [json.loads(r[0]) for r in rows]


def folder(pid):
    if not __import__("re").fullmatch(r"[0-9a-f]{32}", pid):
        raise ValueError("Invalid project ID")
    path = DATA / pid
    path.mkdir(exist_ok=True)
    return path


def safe_file(pid, name):
    base = (folder(pid) / "source").resolve()
    path = (base / name).resolve()
    if not path.is_relative_to(base) or path == base:
        raise ValueError("Invalid file path")
    return path


def write(pid, name, content):
    path = safe_file(pid, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
