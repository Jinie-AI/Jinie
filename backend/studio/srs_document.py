"""Shared SRS content for the website, PDF and Markdown exports."""
def build_srs(p):
    requirements = p.get("requirements", [])
    pages = list(dict.fromkeys(r["page"] for r in requirements))
    configs = p.get("screen_configs") or p.get("spec", {}).get("screen_configs", {})
    sections = []
    def add(title, note, entries):
        sections.append({"title": title, "note": note, "entries": entries})
    add("1. Scope and approval", "This specification describes the saved project revision. Approval does not certify production readiness.", [
        p.get("prompt", "No brief supplied."),
        f"Revision: {p.get('revision', 1)} | Build revision: {p.get('build_revision') or 'Not built'}",
        f"Requirements accepted: {sum(bool(r.get('approved')) for r in requirements)} of {len(requirements)}",
    ])
    add("2. Functional Requirements (FR)", "Requirement IDs remain stable for traceability. Acceptance checks are proposed checks, not recorded test passes.", [
        f"{r.get('id', 'FR')} | {r['page']} | {'Accepted' if r.get('approved') else 'Pending review'}\n{r.get('text', '')}\nAcceptance: open the {r['page']} screen and verify the behavior described above against the accepted screen design."
        for r in requirements
    ])
    add("3. Non-Functional Requirements (NFR)", "Quality targets require measurement on the intended devices before release.", [
        f"{r.get('id', 'NFR')} | {r.get('category', 'Quality')}\n{r.get('text', '')}\nVerification: record a reproducible test and observed result before marking this target satisfied."
        for r in p.get("nfr", [])
    ] or ["No quality targets recorded. Define performance, accessibility, security and recovery criteria before release."])
    tree = ["App -> AppView -> Header / Screen content / Navigation"]
    for page in pages:
        composition = configs.get(page, {}).get("composition")
        if page in ("home", "products") and composition:
            blocks = [b["kind"] for b in composition.get("blocks", [])
                      if not (b["kind"] == "hero" and configs[page].get("show_hero") is False)
                      and not (b["kind"] == "search" and configs[page].get("show_search") is False)]
            tree.append(f"AppView -> {page} -> PlannedCommerce -> " + " / ".join(blocks))
            if "collection" in blocks:
                tree.append(f"{page} -> collection -> ProductCard -> Image / Name / Price / Actions")
        else:
            tree.append(f"AppView -> {page} -> Screen-specific content and controls")
    add("4. Component Tree", "Logical rendering hierarchy derived from the selected screens and saved composition. Retrieved references are design guidance, not automatically installed components.", tree)
    entities = [
        "Product: id, name, price, category, description, image_url, badge, rating. Catalogue records come from generated configuration.",
        "Category: label derived from Product.category. One category groups many products."
    ] if any(x in pages for x in ("home", "products", "detail", "search", "cart", "checkout")) else []
    if "cart" in pages:
        entities += ["CartItem: productId, quantity. Each item references one Product; the local cart contains many items."]
    if any(x in pages for x in ("checkout", "orders")):
        entities += ["Order: local order record, purchased items and total. An order contains product/quantity snapshots. This is a device-local demo record, not a server-confirmed payment."]
    if any(x in pages for x in ("profile", "checkout")):
        entities += ["Customer details: customer name and address in local application state. This does not represent authenticated user accounts."]
    if "settings" in pages:
        entities += ["Preferences: notification preference and local application settings."]
    for page in pages:
        if page.startswith("custom_"):
            fields = [f["label"] for section in configs.get(page, {}).get("sections", []) for f in section.get("fields", [])]
            entities.append(f"{configs.get(page, {}).get('title') or page}: " + ", ".join(fields) + ". Read-only display fields; no remote record service is provisioned.")
    add("5. Entities and Relationships", "Conceptual data model of the generated application; no server database schema is implied.", entities or ["No structured domain entities are defined for the selected screens."])
    sitemap = [f"Application -> {page} | {next((r.get('id', '') for r in requirements if r['page'] == page), '')}" for page in pages]
    for source, target, action in [("products", "detail", "Select product"), ("home", "detail", "Select product"), ("search", "detail", "Select result"), ("detail", "cart", "Add/view cart"), ("cart", "checkout", "Proceed to checkout"), ("checkout", "orders", "View local orders")]:
        if source in pages and target in pages:
            sitemap.append(f"{source} -> {target}: {action}")
    add("6. Sitemap and Navigation", f"Navigation style: {p.get('design', {}).get('navigation', 'bottom')}. Pending screens remain proposed until accepted.", sitemap)
    add("7. Technology Stack", "Generated application and Jinie authoring service are separate systems.", [
        "Generated application: React Native, Expo, React hooks/context, React Native Web.",
        "Device-local persistence: AsyncStorage on native platforms; browser storage on web. No hosted database is provisioned.",
        "Preview compilation: esbuild; saved JSON configuration and validated screen composition.",
        "Jinie website: React, TypeScript and Vite.",
        "Jinie backend: Python, FastAPI and SQLite project storage.",
        "Planning: trained intake/layout models, component retrieval and optional API planning. These authoring dependencies are not an application backend."
    ])
    add("8. Traceability and Release Checks", "A test identifier alone is not evidence of a passed test. Validate all requested integrations before release.", [
        f"{t.get('requirement', '')} -> {t.get('page', '')} -> {', '.join(t.get('files', []))} | Check: {t.get('test', 'Not recorded')}"
        for t in p.get("traceability", [])
    ] + [f"{t.get('id', '')}: {t.get('name', '')} | {t.get('status', 'Not run')}" for t in p.get("tests", [])]
      + ["Release gaps: live payments, server-side authentication, order fulfilment, privacy controls and store publishing require separate integration and verification."])
    return {"name": p.get("name", "Untitled app"), "revision": p.get("revision", 1), "sections": sections}

def srs_markdown(p):
    doc = build_srs(p)
    parts = [f"# {doc['name']} - Software Requirements Specification"]
    for section in doc["sections"]:
        parts += [f"## {section['title']}", section["note"]]
        parts += ["- " + entry.replace("\n", "\n  ") for entry in section["entries"]]
    return "\n\n".join(parts) + "\n"
