import json
import os
import re
from threading import Lock
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_GLOBAL_RAG = None
_RAG_LOCK = Lock()

# Search descriptions supplement the imported API docs, which mostly describe props.
PATTERN_DESCRIPTIONS = {
    "Searchbar": "Search and filter a product catalog by name, category or description.",
    "Card": "Group product imagery, title, price and actions in a catalog card.",
    "CardCover": "Display a product photograph above its catalog details.",
    "Chip": "Filter products by category using compact selectable labels.",
    "Badge": "Highlight a promotional label or item count.",
    "Banner": "Introduce a collection with a hero heading and supporting message.",
    "TextInput": "Collect customer name, delivery address or search text.",
    "Button": "Trigger an action such as add to cart or confirm an order.",
    "IconButton": "Compact action for quantity increase, decrease or removal.",
    "BottomNavigation": "Switch between primary app screens using bottom tabs.",
    "Appbar": "Show the app name, current screen and navigation actions.",
    "Avatar": "Represent a customer on a local profile screen.",
    "Switch": "Toggle a local settings preference on or off.",
    "ListItem": "Present a contact detail, preference or order summary row.",
    "HelperText": "Explain a form field or show a validation error.",
    "Snackbar": "Confirm an action, such as an item added to the shopping bag.",
    "Divider": "Separate order totals and related groups of information.",
}


# Retrieval index: TF-IDF represents catalogue text; cosine similarity ranks components against the search query.
class LocalComponentRAG:
    def __init__(self, catalog_path=None):
        if not catalog_path or not os.path.exists(catalog_path):
            catalog_path = Path(__file__).resolve().parent / "data" / "catalog.json"

        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        self.vectorizer = TfidfVectorizer(
            stop_words="english", token_pattern=r"(?u)\b\w+\b"
        )
        self.corpus = [self._get_searchable_text(c) for c in self.catalog]
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def _get_searchable_text(self, comp):
        name = comp.get("name", "")
        split_name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
        if "Searchbar" in name:
            split_name += " search bar"
        category = comp.get("category", "")
        description = PATTERN_DESCRIPTIONS.get(name, comp.get("description", ""))
        props = " ".join(comp.get("props", []))
        return f"{name} {split_name} {name} {category} {category} {description} {props}"

    def retrieve_components(self, query: str, top_k: int = 5):
        if not query or not query.strip() or top_k <= 0:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][: min(top_k, 20)]

        results = []
        for idx in top_indices:
            score_val = float(scores[idx])
            if score_val <= 0.01:
                continue
            comp = self.catalog[idx]
            results.append(
                {
                    "name": comp.get("name"),
                    "category": comp.get("category"),
                    "score": score_val,
                    "description": PATTERN_DESCRIPTIONS.get(
                        comp.get("name"), comp.get("description", "")
                    ),
                    "props": comp.get("props", [])[:8],
                    "import_path": comp.get("import_path", "react-native-paper"),
                }
            )
        return results


def get_rag_components(query: str, top_k: int = 4):
    global _GLOBAL_RAG
    with _RAG_LOCK:
        if _GLOBAL_RAG is None:
            _GLOBAL_RAG = LocalComponentRAG()
    return _GLOBAL_RAG.retrieve_components(query, top_k)
