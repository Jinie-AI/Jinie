"""Regression checks for reuse and explicit requirements, without paid calls."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from modules.utilities.performance import memoized
from modules.component_generator.screen_contract import normalize_pages
from modules.component_generator import retrieval


def test_cached_results_are_independent_and_misses_are_serialized():
    calls = []

    @memoized(maxsize=2)
    def compute(key):
        calls.append(key)
        return {"nested": []}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(compute, ["same"] * 4))
    assert calls == ["same"]
    results[0]["nested"].append("edited")
    assert compute("same") == {"nested": []}
    compute("second")
    compute("third")
    compute("same")
    assert calls.count("same") == 2


def test_failures_are_not_cached():
    calls = []

    @memoized()
    def fail(key):
        calls.append(key)
        raise ValueError("unavailable")

    for _ in range(2):
        with pytest.raises(ValueError):
            fail("x")
    assert len(calls) == 2


def test_expired_values_are_recomputed():
    calls = []

    @memoized(ttl=0)
    def compute(key):
        calls.append(key)
        return key

    compute("x")
    compute("x")
    assert len(calls) == 2


def test_explicit_core_pages_survive_classifier_omissions():
    pages = normalize_pages(["home"], "Include products, cart and checkout. No search.")
    assert {"products", "detail", "cart", "checkout"} <= set(pages)
    assert "search" not in pages
    assert "checkout" not in normalize_pages(["home"], "Include checkout without cart")


def test_retrieval_reuses_queries_and_keeps_page_associations_independent(monkeypatch):
    retrieval._retrieve_cached.cache_clear()
    retrieval._query_cached.cache_clear()
    calls = []

    def retrieve(query, top_k):
        calls.append(query)
        return [{"name": "Card", "score": 0.7}]

    monkeypatch.setattr(retrieval, "get_rag_components", retrieve)
    try:
        first = retrieval.retrieve_for_screens("unique brief", ["home", "cart"])
        assert len(calls) == 3  # Each screen, plus one shared brief query.
        first[0]["screens"].append("fake")
        second = retrieval.retrieve_for_screens("unique brief", ["home", "cart"])
        assert len(calls) == 3
        assert second[0]["screens"] == ["home", "cart"]
    finally:
        retrieval._retrieve_cached.cache_clear()
        retrieval._query_cached.cache_clear()


def test_intake_reads_later_windows_and_reuses_result(monkeypatch, tmp_path):
    import json
    import torch
    from modules.engine import models

    checkpoint = tmp_path / "intake"
    checkpoint.mkdir()
    (checkpoint / "config.json").write_text("{}")
    (checkpoint / "labels.json").write_text(json.dumps([
        "business:clothing", "business:food", "page:home", "page:checkout"
    ]))
    monkeypatch.setattr(models, "MODEL_DIR", tmp_path)
    calls = []

    class Tokenizer:
        def __call__(self, prompt, **kwargs):
            assert kwargs["return_overflowing_tokens"] is True
            return {"input_ids": torch.tensor([[1, 2], [3, 4]]),
                    "overflow_to_sample_mapping": torch.tensor([0, 0])}

    class Model:
        def eval(self):
            return self

        def __call__(self, **batch):
            from types import SimpleNamespace
            calls.append(batch)
            # Ambiguous business predictions must not replace the rules' food domain.
            return SimpleNamespace(logits=torch.tensor([
                [0.1, 0.0, 3.0, -5.0], [0.1, 0.0, -5.0, 3.0]
            ]))

    monkeypatch.setattr(models, "intake_model", lambda: (Tokenizer(), Model()))
    models.intake.cache_clear()
    try:
        first = models.intake("A food restaurant")
        assert first["business"] == "food"
        assert {"home", "cart", "checkout"} <= set(first["pages"])
        assert "overflow_to_sample_mapping" not in calls[0]
        first["pages"].clear()
        assert models.intake("A food restaurant")["pages"]
        assert len(calls) == 1
    finally:
        models.intake.cache_clear()
