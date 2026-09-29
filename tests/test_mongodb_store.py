import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from studio import store

def test_mongo_save_get_and_list(monkeypatch):
    collection = MagicMock()
    monkeypatch.setattr(store, "mongo_collection", lambda: collection)
    project = {"id": "a", "name": "Shop"}
    store.save(project)
    collection.replace_one.assert_called_once_with(
        {"_id": "a"}, {"_id": "a", "project": project}, upsert=True)
    collection.find_one.return_value = {"_id": "a", "project": project}
    assert store.get("a") == project
    collection.find.return_value.sort.return_value = [{"project": project}]
    assert store.listing() == [project]
    collection.find_one.return_value = None
    with pytest.raises(KeyError):
        store.get("missing")

def test_sqlite_and_non_overwriting_migration(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DATA", tmp_path)
    monkeypatch.setattr(store, "mongo_collection", lambda: None)
    project = {"id": "a", "name": "Original"}
    store.save(project)
    assert store.get("a") == project
    collection = MagicMock()
    collection.update_one.return_value.upserted_id = "a"
    monkeypatch.setattr(store, "mongo_collection", lambda: collection)
    assert store.migrate_sqlite() == 1
    collection.update_one.assert_called_once_with(
        {"_id": "a"}, {"$setOnInsert": {"project": project}}, upsert=True)
    monkeypatch.setattr(store, "mongo_collection", lambda: None)
    assert store.get("a") == project
