"""Shared, executable scope for planning, review and generated screens."""

import re
from typing import Literal

PageId = Literal[
    "home",
    "products",
    "detail",
    "cart",
    "checkout",
    "contact",
    "about",
    "search",
    "settings",
    "profile",
]
BusinessId = Literal[
    "clothing",
    "food",
    "flowers",
    "electronics",
    "accessories",
    "furniture",
    "beauty",
    "books",
    "repair",
    "jewellery",
    "services",
]

CAPABILITIES = {
    "home": "Hero title/subtitle, product cards, optional search, category filters.",
    "products": "Product catalog with category filtering, names, prices and images.",
    "detail": "Product image, description, category, price and add-to-bag when cart exists.",
    "cart": "Increase/decrease quantities, remove items, subtotal; checkout if enabled.",
    "checkout": "Name and address validation, local cash-on-delivery demo order.",
    "search": "Search product names, categories and descriptions with an empty state.",
    "contact": "Contact information; placeholder details need owner review.",
    "about": "Brand story and description.",
    "settings": "Local demo preference toggle and clear local shopping data; no push delivery.",
    "profile": "Device-local customer details and order summary; no account authentication.",
}

PAGE_ALIASES = {
    "home": r"home(?:page)?",
    "products": r"products?|catalog(?:ue)?|shop|menu",
    "detail": r"(?:product )?details?",
    "cart": r"cart|shopping bag|basket",
    "checkout": r"checkout|check out",
    "search": r"search",
    "contact": r"contact(?: us)?",
    "about": r"about(?: us)?",
    "settings": r"settings?|preferences",
    "profile": r"(?:user )?profile|account",
}


def excluded_pages(prompt):
    text = prompt.casefold().replace("’", "'")
    excluded = set()
    negative = r"(?:no|without|do not want|don't want|do not need|don't need|not need|exclude|omit|remove)"
    for page, aliases in PAGE_ALIASES.items():
        target = r"(?:" + aliases + r")"
        if re.search(
            r"\b" + negative + r"\s+(?:a |an |the |any )?" + target + r"\b", text
        ):
            excluded.add(page)
        if re.search(
            r"\b" + target + r"\s+(?:screen |page )?(?:nahi|nahin|mat)\b", text
        ):
            excluded.add(page)
    if "cart" in excluded:
        excluded.add("checkout")
    return excluded


def normalize_pages(pages, prompt):
    excluded = excluded_pages(prompt)
    result = [
        page
        for page in dict.fromkeys(pages)
        if page in CAPABILITIES and page not in excluded
    ]
    # Explicit screens must survive a classifier's incomplete or uncertain labels.
    for page in CAPABILITIES:
        if (
            page not in excluded
            and re.search(r"\b(?:" + PAGE_ALIASES[page] + r")\b", prompt.casefold())
            and page not in result
        ):
            result.append(page)
    if "checkout" in result and "cart" not in result:
        result.insert(result.index("checkout"), "cart")
    if "products" in result and "detail" not in result and "detail" not in excluded:
        result.insert(result.index("products") + 1, "detail")
    if not result:
        result = [next((page for page in CAPABILITIES if page not in excluded), "home")]
    return result
