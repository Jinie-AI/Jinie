"""
catalog.py

RUNTIME loader — reads data/catalog.json (produced by
ingestion/extract_components.py) into typed Python objects. Nothing
in here reads .tsx files directly; that's ingestion's job. This file
only loads the already-extracted, already-real data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, TypedDict


class ComponentEntry(TypedDict):
    name: str
    category: str
    props: List[str]
    description: str
    import_path: str
    source_file: str


def load_catalog() -> List[ComponentEntry]:
    catalog_path = Path(__file__).resolve().parent / "data" / "catalog.json"
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"{catalog_path} not found. Run ingestion/extract_components.py first."
        )
    return json.loads(catalog_path.read_text(encoding="utf-8"))


CATALOG: List[ComponentEntry] = load_catalog()