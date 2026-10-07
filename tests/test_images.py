"""Photo search regressions with no real credentials or network requests."""
import sys
from copy import deepcopy
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from modules.component_generator import images


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    images._search_batch.cache_clear()
    monkeypatch.delenv("UNSPLASH_ACCESS_KEY", raising=False)
    monkeypatch.setattr(images, "_track", lambda urls: None)
    yield
    images._search_batch.cache_clear()


def catalog():
    return {"products": [{"id": "one", "name": "Laptop", "category": "Computers", "image_url": "original"}]}


def photo():
    return {"id": "photo-one", "urls": {"small": "https://images.unsplash.com/photo-example?ixid=keep-me"},
            "user": {"name": "Photographer", "links": {"html": "https://unsplash.com/@photographer"}},
            "links": {"html": "https://unsplash.com/photos/example", "download_location": "https://api.unsplash.com/photos/example/download"}}


def test_missing_key_keeps_existing_images(monkeypatch):
    monkeypatch.setattr(images, "_search", lambda query: pytest.fail("Unexpected network search"))
    spec = catalog()
    assert images.assign_product_images(spec)["matched"] == 0
    assert spec["products"][0]["image_url"] == "original"


def test_photo_search_is_cached_and_credits_are_preserved(monkeypatch):
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "test-only")
    queries = []
    def search(query):
        queries.append(query)
        return [photo()]
    monkeypatch.setattr(images, "_search", search)
    first, second = catalog(), catalog()
    assert images.assign_product_images(first)["matched"] == 1
    first["products"][0]["image_credit"]["name"] = "Edited"
    assert images.assign_product_images(second)["matched"] == 1
    assert queries == ["Laptop Computers"]
    assert "ixid=keep-me" in second["products"][0]["image_url"]
    assert second["products"][0]["image_credit"]["name"] == "Photographer"
    assert "utm_source=jinie" in second["products"][0]["image_credit"]["url"]


def test_failed_search_and_untrusted_urls_keep_fallback(monkeypatch):
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "test-only")
    def fail(query):
        raise httpx.ConnectError("Unavailable")
    monkeypatch.setattr(images, "_search", fail)
    spec = catalog()
    assert images.assign_product_images(spec)["matched"] == 0
    assert spec["products"][0]["image_url"] == "original"
    bad = deepcopy(photo())
    bad["urls"]["small"] = "https://untrusted.example/image"
    monkeypatch.setattr(images, "_search", lambda query: [bad])
    assert images.assign_product_images(spec)["matched"] == 0
    assert spec["products"][0]["image_url"] == "original"
