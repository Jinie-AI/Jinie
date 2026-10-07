"""Render functional requirements from saved screen requirements and configurations."""


def _acceptance_check(page, config):
    sections = config.get("sections", [])
    fields = [field.get("label", "") for section in sections for field in section.get("fields", [])]
    fields = [field for field in fields if field]
    if fields:
        return f"Open {page} and verify these requested fields are visible: {', '.join(fields)}."

    composition = config.get("composition") or {}
    blocks = [block.get("kind", "") for block in composition.get("blocks", [])]
    blocks = [block for block in blocks if block]
    if config.get("show_hero") is False:
        blocks = [block for block in blocks if block != "hero"]
    if config.get("show_search") is False:
        blocks = [block for block in blocks if block != "search"]
    if blocks:
        return f"Open {page} and verify the configured {', '.join(blocks)} sections render in their saved order and their controls respond."

    title = config.get("title") or page.replace("_", " ").title()
    return f"Open {page}, verify the {title} content renders, and exercise every visible control described by this requirement."


# Functional requirements: describe selected-screen behavior and acceptance checks linked to the originating requirement.
def generate_functional_requirements(requirements, screen_configs=None):
    """Keep traceability IDs while grounding checks in the accepted screen plan."""
    screen_configs = screen_configs or {}
    entries = []
    for requirement in requirements:
        page = requirement["page"]
        status = "Accepted" if requirement.get("approved") else "Pending review"
        entries.append(
            f"{requirement.get('id', 'FR')} | {page} | {status}\n"
            f"{requirement.get('text', '')}\n"
            f"Acceptance: {_acceptance_check(page, screen_configs.get(page, {}))}"
        )
    return entries
