"""Keep regression tests away from the configured live project database."""
import pytest

@pytest.fixture(autouse=True)
def isolate_live_database(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
