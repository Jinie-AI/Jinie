"""Module 08: timestamped generation events and persistence."""
from datetime import datetime, timezone
from modules.utilities import store

def now():
    return datetime.now(timezone.utc).isoformat()

def log(p, stage, message):
    p["events"].append(
        {"id": len(p["events"]) + 1, "time": now(), "stage": stage, "message": message}
    )
    p["updated_at"] = now()
    store.save(p)
