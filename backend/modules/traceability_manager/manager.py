"""Module 03: map approved requirements to generated artifacts and checks."""

def build_traceability(p, config, components, screen_configs, rag_comps):
    rag_by_page = {
        page: [c["id"] for c in components if page in c.get("screens", [])]
        for page in config["pages"]
    }
    return [
        {
            "requirement": r["id"],
            "page": r["page"],
            "components": (
                ["CMP-001"]
                if r["page"] in ["home", "products", "search"]
                else []
            ),
            "references": rag_by_page.get(r["page"], []),
            "files": ["App.jsx", "src/config.json", "src/components/AppView.jsx"]
            + (["src/components/PlannedCommerce.jsx"] if r["page"] in ("home", "products") and screen_configs.get(r["page"], {}).get("composition") else [])
            + (["src/components/ProductCard.jsx"] if r["page"] in ("home", "products", "search") else [])
            + (["src/rag_components.json"] if rag_comps else []),
            "test": f"TEST-{i + 1:03}",
        }
        for i, r in enumerate(p["requirements"])
        if r["approved"]
    ]
