"""Shared helper functions (naming, slugs) used across the compiler package."""

from __future__ import annotations

import re
from pathlib import Path

from .constants import _NAME_SPLIT_RE, _SLUG_SANITIZE_RE


def slugify(value: str) -> str:
    """Convert a string into a URL/package-safe slug (lowercase, hyphenated)."""
    value = value.strip().lower().replace("_", "-").replace(" ", "-")
    value = _SLUG_SANITIZE_RE.sub("-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def to_pascal_case(filename: str) -> str:
    """Derive a PascalCase component identifier from a filename or string.

    Preserves existing internal casing (so 'HomeScreen.tsx' -> 'HomeScreen',
    not 'Homescreen' as `str.title()` would produce), while still handling
    snake_case / kebab-case / space-separated input.
    """
    stem = Path(filename).stem
    parts = [p for p in _NAME_SPLIT_RE.split(stem) if p]
    if not parts:
        return "Component"
    return "".join(p[0].upper() + p[1:] for p in parts)


def to_screen_component_name(filename: str) -> str:
    """Derive the exported screen function name, ensuring a single 'Screen'
    suffix rather than duplicating it (e.g. 'HomeScreen.tsx' -> 'HomeScreen',
    not 'HomeScreenScreen'; 'Home.tsx' -> 'HomeScreen').
    """
    name = to_pascal_case(filename)
    return name if name.endswith("Screen") else f"{name}Screen"
