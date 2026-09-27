"""Real local index checks, without model downloads or external services."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from component_library.retrieverRAG import LocalComponentRAG
from studio.retrieval import retrieve_for_screens


def test_empty_and_unrelated_queries_do_not_return_fake_matches():
    rag = LocalComponentRAG()
    assert rag.retrieve_components("") == []
    assert rag.retrieve_components("zzzzqqqqxxxx") == []
    assert rag.retrieve_components("search", -1) == []


def test_search_retrieves_relevant_component():
    results = LocalComponentRAG().retrieve_components("search filter catalog", 3)
    assert "Searchbar" in {item["name"] for item in results}
    assert all(item["score"] > 0 for item in results)


def test_screen_matches_have_real_associations():
    results = retrieve_for_screens("Minimal clothing shop", ["products", "checkout"])
    assert len(results) == len({item["name"] for item in results})
    assert all(set(item["screens"]) <= {"products", "checkout"} for item in results)
    assert any(
        item["name"] == "TextInput" and "checkout" in item["screens"]
        for item in results
    )
