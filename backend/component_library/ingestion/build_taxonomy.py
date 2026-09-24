"""
build_taxonomy.py

Groups the extracted catalog.json into a real category tree, saved as
taxonomy.json. This is the "DSA tree" — lets retrieval narrow down to
a branch (e.g. "Inputs") before searching, instead of scanning the
entire flat catalog every time.

Run AFTER extract_components.py:
    cd backend/component_library
    python ingestion/build_taxonomy.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def build_taxonomy(catalog: list[dict]) -> dict[str, list[str]]:
    tree: dict[str, list[str]] = defaultdict(list)
    for entry in catalog:
        tree[entry["category"]].append(entry["name"])
    return dict(sorted(tree.items()))


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent  # backend/component_library/
    catalog_path = project_root / "data" / "catalog.json"
    output_path = project_root / "data" / "taxonomy.json"

    if not catalog_path.exists():
        raise SystemExit(f"ERROR: {catalog_path} not found. Run extract_components.py first.")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    taxonomy = build_taxonomy(catalog)

    output_path.write_text(json.dumps(taxonomy, indent=2), encoding="utf-8")

    print("Taxonomy built:")
    for category, names in taxonomy.items():
        print(f"  {category}: {len(names)} components -> {', '.join(names)}")
    print(f"\nWritten to {output_path}")