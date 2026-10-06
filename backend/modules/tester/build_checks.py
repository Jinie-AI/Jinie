"""Small deterministic checks; never label these as behavioural/device tests."""
import json
from modules.component_generator.composition import Composition
from modules.component_generator.screen_contract import CAPABILITIES
from modules.component_generator.custom_screens import InformationSection
import re

def check_artifacts(source, preview, config):
    results = []
    def record(identifier, name, passed):
        results.append({"id": identifier, "requirement": None, "name": name,
                        "status": "passed" if passed else "failed", "kind": "structural"})
    required = ["App.jsx", "index.js", "package.json", "src/config.json",
                "src/components/AppView.jsx", "src/components/ProductCard.jsx",
                "src/storage.js", "src/storage.web.js"]
    record("FILES-001", "Required project files exist and are non-empty",
           all((source / f).is_file() and (source / f).stat().st_size > 0 for f in required))
    record("PREVIEW-001", "Preview HTML and JavaScript artifacts exist",
           all((preview / f).is_file() and (preview / f).stat().st_size > 0 for f in ("index.html", "app.js")))
    pages = config.get("pages", [])
    record("ROUTES-001", "Screen IDs are supported, unique and include checkout dependencies",
           bool(pages) and all(p in CAPABILITIES or re.fullmatch(r"custom_[a-z][a-z0-9_]{0,39}", p) for p in pages)
           and len(pages) == len(set(pages))
           and ("checkout" not in pages or "cart" in pages))
    valid = True
    configs = config.get("screen_configs") or {}
    for page in pages:
        if page.startswith("custom_"):
            sections = configs.get(page, {}).get("sections", [])
            try:
                if not sections:
                    valid = False
                for section in sections:
                    InformationSection.model_validate(section)
            except (ValueError, TypeError):
                valid = False
        composition = configs.get(page, {}).get("composition")
        if composition:
            try:
                Composition.model_validate(composition)
            except (ValueError, TypeError):
                valid = False
            if page in ("home", "products") and not (source / "src/components/PlannedCommerce.jsx").is_file():
                valid = False
    record("LAYOUT-001", "Saved compositions validate and required renderer exists", valid)
    try:
        json.loads((source / "package.json").read_text(encoding="utf-8"))
        package_valid = True
    except (OSError, ValueError):
        package_valid = False
    record("PACKAGE-001", "Exported package manifest is valid JSON", package_valid)
    return results
