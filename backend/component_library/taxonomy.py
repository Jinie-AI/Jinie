"""
taxonomy.py

RUNTIME loader — reads data/taxonomy.json (produced by
ingestion/build_taxonomy.py) into a simple, real tree structure. This
is the actual DSA piece: a dict-of-lists where each category maps to
the component names inside it, letting you narrow a search to one
branch instead of scanning the whole catalog.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def load_taxonomy() -> Dict[str, List[str]]:
    taxonomy_path = Path(__file__).resolve().parent / "data" / "taxonomy.json"
    if not taxonomy_path.exists():
        raise FileNotFoundError(
            f"{taxonomy_path} not found. Run ingestion/build_taxonomy.py first."
        )
    return json.loads(taxonomy_path.read_text(encoding="utf-8"))


TAXONOMY: Dict[str, List[str]] = load_taxonomy()


def category_for(component_name: str) -> Optional[str]:
    """Given a component name, returns which category branch it belongs to."""
    for category, names in TAXONOMY.items():
        if component_name in names:
            return category
    return None


def components_in_category(category: str) -> List[str]:
    """Returns all component names within one category branch."""
    return TAXONOMY.get(category, [])