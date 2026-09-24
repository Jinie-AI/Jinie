"""
retriever.py

Local, free retrieval over the REAL component catalog (extracted from
your actual downloaded React Native Paper source). No API calls, no
internet — TF-IDF text matching, fit once at import time.

IMPORTANT: retrieval quality depends entirely on catalog.json's
description text having good keyword overlap with what you search for.
If a component your screen obviously needs (e.g. TextInput for a login
screen) doesn't show up in results, the fix is almost always: improve
that component's description in the extraction step, or manually patch
data/catalog.json with a richer description — this is a known,
expected limitation of TF-IDF, not a bug.
"""

from __future__ import annotations

from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .catalog import CATALOG, ComponentEntry
except ImportError:
    from catalog import CATALOG, ComponentEntry


def _searchable_text(entry: ComponentEntry) -> str:
    return f"{entry['name']} {entry['category']} {entry['description']} {' '.join(entry['props'])}"


_CORPUS = [_searchable_text(entry) for entry in CATALOG]
_VECTORIZER = TfidfVectorizer(stop_words="english")
_MATRIX = _VECTORIZER.fit_transform(_CORPUS)


def retrieve_components(query_text: str, top_k: int = 8) -> List[ComponentEntry]:
    if not query_text or not query_text.strip():
        return []
    query_vector = _VECTORIZER.transform([query_text])
    scores = cosine_similarity(query_vector, _MATRIX)[0]
    ranked_indices = scores.argsort()[::-1][:top_k]
    return [CATALOG[i] for i in ranked_indices]


def format_for_prompt(entries: List[ComponentEntry]) -> str:
    lines = []
    for entry in entries:
        props_str = ", ".join(entry["props"][:8]) if entry["props"] else "(no props extracted)"
        lines.append(f"- {entry['name']} ({entry['category']}): {entry['description']} [props: {props_str}]")
    return "\n".join(lines)