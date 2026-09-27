"""Retrieve screen-specific references from the existing local component index."""

from component_library.retrieverRAG import get_rag_components

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
    matches = {}
    for page in pages:
        query = SCREEN_QUERIES.get(page, page) + " " + prompt[:1200]
        for item in get_rag_components(query, top_k=3):
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
