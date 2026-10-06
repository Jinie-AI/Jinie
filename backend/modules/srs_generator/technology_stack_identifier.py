"""Identify the implementation stack required by the saved application plan."""


def identify_technology_stack(spec=None):
    """Return technologies actually used by the generated project."""
    spec = spec or {}
    pages = set(spec.get("pages", []))
    stack = ["React Native", "Expo SDK 54", "React Context / hooks"]
    if pages & {"cart", "checkout", "orders", "profile", "settings"}:
        stack.append("AsyncStorage")
    stack.append("React Native Web preview")
    return stack

def technology_stack_entries(project):
    spec = project.get("spec", {})
    selected = project.get("stack") or identify_technology_stack(spec)
    entries = [f"Generated application technology: {item}." for item in selected]
    entries.extend([
        "Preview build pipeline: esbuild compiles the generated React Native Web source after structural validation.",
        "Jinie authoring website: React, TypeScript and Vite.",
        "Jinie authoring backend: Python and FastAPI with local project storage.",
    ])
    if "AsyncStorage" not in selected:
        entries.append("No persistent application data store is required by the currently selected screens.")
    return entries
