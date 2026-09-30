"""Retrieve screen-specific references from the existing local component index."""

from component_library.retrieverRAG import get_rag_components
from .performance import memoized
from .screen_contract import CAPABILITIES

SCREEN_QUERIES = {
    "home": "Banner Card CardCover Chip Searchbar product collection",
    "products": "Card CardCover Chip Searchbar product catalog",
    "detail": "CardCover CardContent Button Badge product detail",
    "cart": "ListItem IconButton Button Divider cart quantity total",
    "checkout": "TextInput HelperText Button delivery address order",
    "search": "Searchbar Card Chip search catalog",
    "contact": "ListItem IconButton contact information",
    "about": "CardCover Text brand story",
    "settings": "Switch ListItem Button local preference",
    "profile": "Avatar ListItem TextInput customer profile",
}


def retrieve_for_screens(prompt, pages):
    return _retrieve_cached(prompt, tuple(dict.fromkeys(pages)))


@memoized(maxsize=64)
def _retrieve_cached(prompt, pages):
    matches = {}
    for page in pages:
        # The complete brief contributes context without overwhelming the screen's purpose.
        screen_query = SCREEN_QUERIES.get(page, page) + " " + CAPABILITIES.get(page, "")
        ranked = {}
        for query, weight in ((screen_query, 0.8), (prompt, 0.2)):
            for item in _query_cached(query):
                entry = ranked.setdefault(item["name"], {**item, "score": 0.0})
                entry["score"] += weight * item["score"]
        selected = sorted(ranked.values(), key=lambda item: (-item["score"], item["name"]))[:3]
        for item in selected:
            entry = matches.setdefault(item["name"], {**item, "screens": []})
            entry["planning_role"] = (
                "search" if "search" in item["name"].lower() else
                "categories" if "chip" in item["name"].lower() else
                "hero / spotlight" if any(word in item["name"].lower() for word in ("cover", "image", "banner")) else
                "collection / supporting content"
            )
            entry["score"] = max(entry["score"], item["score"])
            if page not in entry["screens"]:
                entry["screens"].append(page)
    return sorted(matches.values(), key=lambda item: (-item["score"], item["name"]))


@memoized(maxsize=128)
def _query_cached(query):
    return get_rag_components(query, top_k=12)
