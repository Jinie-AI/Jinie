"""Shared SRS content for the website, PDF and Markdown exports."""
from .functional_requirement_generator import generate_functional_requirements
from .non_functional_requirement_generator import non_functional_requirement_entries
from .sitemap_generator import generate_sitemap
from .technology_stack_identifier import technology_stack_entries
from .component_tree_generator import generate_component_tree
from .entity_generator import generate_entities

# Shared SRS document: builds structured sections used by the website and document exports from saved project data.
def build_srs(p):
    requirements = p.get("requirements", [])
    configs = p.get("screen_configs") or p.get("spec", {}).get("screen_configs", {})
    sections = []
    def add(title, note, entries):
        sections.append({"title": title, "note": note, "entries": entries})
    add("1. Scope and approval", "This specification describes the saved project revision. Approval does not certify production readiness.", [
        p.get("prompt", "No brief supplied."),
        f"Revision: {p.get('revision', 1)} | Build revision: {p.get('build_revision') or 'Not built'}",
        f"Requirements accepted: {sum(bool(r.get('approved')) for r in requirements)} of {len(requirements)}",
    ])
    add("2. Functional Requirements (FR)", "Requirement IDs remain stable for traceability. Acceptance checks are derived from the saved screen configuration and are not recorded test passes.", generate_functional_requirements(requirements, configs))
    add("3. Non-Functional Requirements (NFR)", "Quality targets require measurement on the intended devices before release.", non_functional_requirement_entries(p.get("nfr", [])))
    tree = generate_component_tree(requirements, configs)
    add("4. Component Tree", "Logical rendering hierarchy derived from the selected screens and saved composition. Retrieved references are design guidance, not automatically installed components.", tree)
    entities = generate_entities(requirements, configs)
    add("5. Entities and Relationships", "Conceptual data model of the generated application; no server database schema is implied.", entities)
    sitemap = generate_sitemap(requirements)
    add("6. Sitemap and Navigation", f"Navigation style: {p.get('design', {}).get('navigation', 'bottom')}. Pending screens remain proposed until accepted.", sitemap)
    add("7. Technology Stack", "Stack entries are derived from the saved project and describe technologies used by this build.", technology_stack_entries(p))
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
