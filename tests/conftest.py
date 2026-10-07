"""Keep regression tests away from the configured live project database."""
import pytest

@pytest.fixture(autouse=True)
def isolate_live_database(monkeypatch, request):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    if not request.module.__name__.endswith("test_firebase_auth"):
        monkeypatch.delenv("FIREBASE_WEB_API_KEY", raising=False)
