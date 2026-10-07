"""Shared, executable scope for planning, review and generated screens."""

import re
from typing import Literal, Annotated
from pydantic import StringConstraints

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
] | Annotated[str, StringConstraints(pattern=r"^custom_[a-z][a-z0-9_]{0,39}$")]
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
    "home": r"home(?:page|screen)?",
    "products": r"products?|catalog(?:ue)?|shop|menu|clothes?|clothing|apparel|laptop models?|phone models?|items?",
    "detail": r"(?:product )?details?",
    "cart": r"cart|shopping bag|basket",
    "checkout": r"checkout|check out",
    "search": r"search",
    "contact": r"contact(?: us)?",
    "about": r"about(?: us)?",
    "settings": r"settings?|preferences",
    "profile": r"(?:user )?profile|account",
}

_GENERIC_SCREEN_WORDS = {
    "screen", "page", "new", "another", "different", "custom", "any", "kind",
    "application", "app", "mobile", "website",
}


def _custom_page_slug(label):
    label = re.sub(r"['’]s\b", "", label.casefold())
    label = re.sub(r"[^a-z0-9]+", "_", label).strip("_")
    return ("custom_" + label[:32].rstrip("_")) if label else ""


def requested_custom_pages(prompt):
    """Find explicitly named screens that are outside the trained page labels."""
    text = prompt.casefold().replace("’", "'")
    found = []
    for segment in re.split(r"[,;.\n]|\band\b", text):
        if re.search(r"\b(?:each|every|all|these|those)\s+(?:screen|page)|\b(?:screen|page)'s\b", segment):
            continue
        if not re.search(r"\b(?:screen|page)\b", segment):
            continue
        negative = re.search(
            r"\b(?:no|without|exclude|omit|remove|don'?t|do not)\b", segment
        )
        if negative:
            continue
        for match in re.finditer(
            r"(?P<label>[a-z][a-z0-9'&/-]*(?:\s+[a-z][a-z0-9'&/-]*){0,6})\s+(?:screen|page)\b",
            segment,
        ):
            label = match.group("label").strip()
            # Keep only the words after prompt-control phrases.
            label = re.split(
                r"\b(?:with|add|include|including|want|need|create|show|provide|for|give me)\b",
                label,
            )[-1].strip()
            label = re.sub(r"^(?:me\s+)?(?:a|an|the|another)\s+", "", label).strip()
            if not label or label in {"a", "an", "the", "me"} or set(label.split()) <= _GENERIC_SCREEN_WORDS:
                continue
            if any(re.fullmatch(aliases, label) for aliases in PAGE_ALIASES.values()):
                continue
            slug = _custom_page_slug(label)
            if slug and slug not in found:
                found.append(slug)
    return found


def excluded_pages(prompt):
    text = prompt.casefold().replace("’", "'")
    excluded = set()
    negative = r"(?:no|without|(?:do not|don'?t)\s+(?:want|need|add|include|show|create)|not need|exclude|omit|remove)"
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


# Screen contract: reconciles model suggestions with requested screens, exclusions and navigation dependencies.
def normalize_pages(pages, prompt):
    excluded = excluded_pages(prompt)
    custom = requested_custom_pages(prompt)
    explicit = [page for page, aliases in PAGE_ALIASES.items()
                if page not in excluded and re.search(r"\b(?:" + aliases + r")\s*(?:screen|page)\b", prompt.casefold())]
    # Match complete items in requested lists, not incidental words inside fields
    # (for example 'contact number' on a doctor page is not a Contact screen).
    for sentence in re.split(r"[.;\n]", prompt.casefold()):
        for item in re.split(r",|\band\b", sentence):
            label = re.split(r"\b(?:with|include|including|add)\b", item)[-1].strip()
            label = re.sub(r"^(?:a|an|the)\s+", "", label)
            label = re.sub(r"\s+(?:screens?|pages?)$", "", label)
            for page, aliases in PAGE_ALIASES.items():
                if page not in excluded and re.fullmatch(aliases, label):
                    explicit.append(page)
    if re.search(r"\buser profile\b", prompt, re.I) and "profile" not in excluded:
        explicit.append("profile")
    explicit = list(dict.fromkeys(explicit))
    listed = len(explicit) + len(custom) >= 2
    if listed:
        pages = explicit + [page for page in pages if page.startswith("custom_")]
    result = [
        page
        for page in dict.fromkeys(pages)
        if (page in CAPABILITIES or re.fullmatch(r"custom_[a-z][a-z0-9_]{0,39}", page)) and page not in excluded
        and not re.match(r"^custom_(?:keep_each|each|every|all|these|those)(?:_|$)", page)
    ]
    # Explicit screens must survive a classifier's incomplete or uncertain labels.
    for page in CAPABILITIES:
        if (
            page not in excluded and (not listed or page in explicit or page in {"cart", "checkout", "detail"})
            and re.search(r"\b(?:" + PAGE_ALIASES[page] + r")\b", prompt.casefold())
            and page not in result
        ):
            result.append(page)
    for page in custom:
        if page not in result:
            result.append(page)
    # A shopping catalogue needs a bag even when a brief lists only top-level screens.
    # Explicit read-only/catalogue-only requests and exclusions take precedence.
    browsing_only = re.search(r"\b(?:read.only|catalog(?:ue)? only|brows(?:e|ing) only|no purchasing|without purchasing)\b", prompt, re.I)
    if "products" in result and "cart" not in excluded and not browsing_only:
        if re.search(r"\b(?:shop|store|buy|purchase|shopping|add.to.(?:cart|bag))\b", prompt, re.I) and "cart" not in result:
            result.append("cart")
    if "checkout" in result and "cart" not in result:
        result.insert(result.index("checkout"), "cart")
    # Product cards navigate to detail. Preserve that interaction even when the
    # customer calls the catalogue something domain-specific such as clothes or laptop models.
    if "products" in result and "detail" not in result and "detail" not in excluded:
        result.insert(result.index("products") + 1, "detail")
    if not result:
        result = [next((page for page in CAPABILITIES if page not in excluded), "home")]
    return result
