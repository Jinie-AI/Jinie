"""Build the SRS component hierarchy from the accepted screen configuration."""


def generate_component_tree(requirements, screen_configs):
    pages = list(dict.fromkeys(item["page"] for item in requirements))
    tree = ["App -> AppView -> Header / Screen content / Navigation"]
    for page in pages:
        config = screen_configs.get(page, {})
        composition = config.get("composition")
        if page in ("home", "products") and composition:
            blocks = [
                block["kind"]
                for block in composition.get("blocks", [])
                if not (block["kind"] == "hero" and config.get("show_hero") is False)
                and not (block["kind"] == "search" and config.get("show_search") is False)
            ]
            tree.append(f"AppView -> {page} -> PlannedCommerce -> " + " / ".join(blocks))
            if "collection" in blocks:
                tree.append(f"{page} -> collection -> ProductCard -> Image / Name / Price / Actions")
        elif page.startswith("custom_"):
            sections = config.get("sections", [])
            labels = [field.get("label", "Field") for section in sections for field in section.get("fields", [])]
            tree.append(f"AppView -> {page} -> Information sections -> " + " / ".join(labels))
        else:
            tree.append(f"AppView -> {page} -> Screen-specific content and controls")
    return tree
