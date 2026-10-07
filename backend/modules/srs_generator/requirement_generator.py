"""Create traceable screen requirements from the Engine's normalized plan."""
from modules.component_generator.screen_contract import CAPABILITIES
from modules.traceability_manager.id_assigner import IDAssigner


# Requirement numbering: converts the selected application specification into reviewable requirements with traceability IDs.
def generate_requirements(spec):
    """Preserve selected screens, planner descriptions and initial approval state."""
    custom_reqs = spec.get("page_requirements", {})
    assigner = IDAssigner()
    return [
        {
            "id": assigner.generate_id("", "REQ"),
            "page": page,
            "text": custom_reqs.get(page)
            or CAPABILITIES.get(page)
            or f"Provide the {page} screen.",
            "approved": False,
        }
        for page in spec["pages"]
    ]
