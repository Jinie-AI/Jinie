"""Generate quality requirements from the actual application specification."""


# Non-functional requirements: records quality targets for the application; targets are not proof that performance has been measured.
def generate_non_functional_requirements(spec, design=None):
    """Return measurable targets relevant to the selected screens and features."""
    pages = set(spec.get("pages", []))
    features = set(spec.get("features", []))
    design = design or spec.get("design", {})
    requirements = [
        {
            "category": "Performance",
            "text": "The generated application shall render its first usable screen within 1,500 ms on the target test device, measured from launch to the first interactive control.",
        },
        {
            "category": "Accessibility",
            "text": "Every interactive control on the selected screens shall expose an accessible label and provide a minimum 44 x 44 dp touch target.",
        },
        {
            "category": "Responsiveness",
            "text": "Every selected screen shall remain readable and operable on phone, tablet and desktop preview sizes without horizontal clipping.",
        },
    ]
    if pages & {"cart", "checkout", "orders", "profile", "settings"} or features & {"cart", "checkout"}:
        requirements.append({
            "category": "Reliability",
            "text": "Locally editable application state shall survive an application restart and shall recover safely when stored data is missing or invalid.",
        })
    if pages & {"checkout", "profile", "custom_medical_record"}:
        requirements.append({
            "category": "Security & Privacy",
            "text": "Personal or transaction fields shall remain device-local in this generated prototype and shall not be written to logs or embedded in generated source code.",
        })
    if design.get("theme") in {"dark", "system"}:
        requirements.append({
            "category": "Visual Accessibility",
            "text": "Text and interactive controls shall remain legible in every configured theme, with visible focus, pressed and disabled states.",
        })
    return [dict(item, id=f"NFR-{index:03}") for index, item in enumerate(requirements, 1)]


def non_functional_requirement_entries(requirements):
    return [
        f"{r.get('id', 'NFR')} | {r.get('category', 'Quality')}\n{r.get('text', '')}\nVerification: record a reproducible test and observed result before marking this target satisfied."
        for r in requirements
    ] or ["No quality targets recorded. Define performance, accessibility, security and recovery criteria before release."]
