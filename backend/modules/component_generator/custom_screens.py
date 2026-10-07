"""Validated read-only custom information screens; no invented records or diagnoses."""
import re
from pydantic import BaseModel, ConfigDict, Field
from modules.component_generator.screen_contract import requested_custom_pages


class InformationField(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=80)
    # Values intentionally come from reviewed project data, not generated diagnoses.
    value: str = Field(default="", max_length=500)


class InformationSection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=100)
    fields: list[InformationField] = Field(min_length=1, max_length=20)


def medical_record_request(prompt):
    if not re.search(r"\bmedical record\b", prompt, re.I):
        return None
    if re.search(r"\b(?:no|without|omit|remove|exclude|don'?t add|do not add)\s+(?:a |the )?medical record", prompt, re.I):
        return None
    labels = []
    for pattern, label in ((r"patient name", "Patient name"), (r"patient id", "Patient ID"),
                           (r"patient condition", "Patient condition"), (r"skin colou?r", "Skin colour")):
        if re.search(pattern, prompt, re.I):
            labels.append(label)
    return {"page": "custom_medical_record", "title": "Medical Record", "subtitle": "Record information",
            "sections": [{"title": "Patient details", "fields": [{"label": label, "value": ""} for label in labels or ["Record details"]]}]}


_SCREEN_FIELDS = {
    "doctor": ["Doctor name", "Specialization", "Contact information", "Availability"],
    "warranty": ["Warranty number", "Coverage", "Expiry date", "Status"],
    "invoice": ["Invoice number", "Date", "Total", "Status"],
    "tracking": ["Tracking ID", "Current status", "Estimated delivery", "Latest update"],
    "appointment": ["Service", "Date", "Time", "Status"],
    "recipe": ["Recipe name", "Ingredients", "Instructions", "Preparation time"],
    "course": ["Course title", "Instructor", "Schedule", "Progress"],
    "event": ["Event name", "Date", "Location", "Description"],
    "report": ["Report title", "Date", "Summary", "Status"],
}


def _title(page):
    return page.removeprefix("custom_").replace("_", " ").title()


def _explicit_fields(prompt):
    match = re.search(
        r"\b(?:include|contain|show|display|fields?\s*(?:are|include)?)\s*:?[ ]+(.+?)(?:[.;]|$)",
        prompt,
        re.I,
    )
    if not match:
        return []
    value = re.split(r"\b(?:screen|page)\b", match.group(1), maxsplit=1)[0]
    fields = [re.sub(r"^(?:and|the|a|an)\s+", "", item.strip(), flags=re.I)
              for item in re.split(r",|\band\b", value, flags=re.I)]
    return [field[:80].strip().capitalize() for field in fields if 1 < len(field.strip()) <= 80][:12]


def generic_screen_request(prompt, page, use_explicit_fields=False):
    title = _title(page)
    lowered = title.casefold()
    fields = _explicit_fields(prompt) if use_explicit_fields else []
    if not fields:
        for keyword, suggestions in _SCREEN_FIELDS.items():
            if keyword in lowered:
                fields = suggestions
                break
    if not fields:
        fields = ["Title", "Description", "Status", "Notes"]
    return {
        "page": page,
        "title": title,
        "subtitle": f"View {title.casefold()} details",
        "layout": "grid" if any(word in lowered for word in ("report", "dashboard", "summary")) else "cards",
        "show_hero": False,
        "show_search": False,
        "show_badges": False,
        "reference_components": [],
        "sections": [{
            "title": "Details",
            "fields": [{"label": label, "value": ""} for label in fields],
        }],
    }


# Custom screens: preserve requested fields and empty initial values; explicit form requests enable local entry and saving.
def complete_custom_screens(prompt, pages, configs, requirements):
    explicit = medical_record_request(prompt)
    if explicit:
        page = next((p for p in pages if p.startswith("custom_") and
                     ("medical" in p or "medical record" in configs.get(p, {}).get("title", "").casefold())), explicit["page"])
        explicit["page"] = page
        if page not in pages:
            pages.append(page)
        # Preserve generated grouping, but ensure every explicitly requested field exists.
        config = configs.setdefault(page, explicit)
        config["title"] = config.get("title") or explicit["title"]
        config["sections"] = config.get("sections") or explicit["sections"]
        found = {f["label"].casefold() for s in config["sections"] for f in s["fields"]}
        missing = [f for f in explicit["sections"][0]["fields"] if f["label"].casefold() not in found]
        if missing:
            config["sections"].append({"title": "Requested details", "fields": missing})
    discovered = requested_custom_pages(prompt)
    custom_pages = list(dict.fromkeys([page for page in pages if page.startswith("custom_")] + discovered))
    for page in discovered:
        if page not in pages:
            pages.append(page)
    for page in custom_pages:
        if page not in configs or not configs[page].get("sections"):
            # Scope fields to their own screen rather than using the first field list
            # in a multi-screen prompt for every page.
            name = page.removeprefix("custom_").replace("_", " ")
            match = re.search(re.escape(name) + r"\s+(?:screen|page)\b([^.;]*)", prompt, re.I)
            context = match.group(1) if match else prompt
            configs[page] = generic_screen_request(context, page, bool(match) or len(custom_pages) == 1)
    for page in pages:
        if not page.startswith("custom_"):
            continue
        config = configs.get(page, {})
        sections = [InformationSection.model_validate(s).model_dump() for s in config.get("sections", [])]
        if not sections:
            raise ValueError("A requested custom screen has no information fields. Please clarify its content.")
        for section in sections:
            for field in section["fields"]:
                field["value"] = ""  # Do not fabricate personal or clinical records.
        config["sections"] = sections
        # Infer behavior from this screen's own sentence, not unrelated screens.
        title_words = page.removeprefix("custom_").replace("_", " ")
        context = next((sentence for sentence in re.split(r"[.;\n]", prompt)
                        if title_words in sentence.casefold()), "")
        readonly = bool(re.search(r"\bread[- ]only\b|\bview only\b|\bdo not (?:edit|save)\b", context, re.I))
        editable = bool(re.search(r"\b(?:form|editable|editing|enter|input|submit|save)\b", context, re.I))
        config["interaction"] = "form" if editable and not readonly else "information"
        labels = [f["label"] for s in sections for f in s["fields"]]
        behavior = (" Allow the user to enter these fields, validate non-empty values and save the record on this device. No remote submission occurs."
                    if config["interaction"] == "form" else " Show Not provided for missing values. This screen is read-only.")
        requirements[page] = f"Display the {config.get('title') or page} screen with labelled fields: " + ", ".join(labels) + "." + behavior
    if len(pages) > 10:
        raise ValueError("This request exceeds the current limit of ten screens. Reduce the requested screens.")
