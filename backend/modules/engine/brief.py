"""Normalize brief whitespace without changing the customer's requirements."""

import re
import unicodedata


def normalize_brief(prompt: str) -> str:
    text = unicodedata.normalize("NFKC", prompt)
    text = re.sub(r"[ \t]+", " ", text).strip()
    if len(text) < 8:
        raise ValueError("Describe the app in at least eight characters")
    return text
