"""Validated read-only custom information screens; no invented records or diagnoses."""
import re
from pydantic import BaseModel, ConfigDict, Field


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
        labels = [f["label"] for s in sections for f in s["fields"]]
        requirements[page] = f"Display the {config.get('title') or page} screen with labelled fields: " + ", ".join(labels) + ". Show Not provided for missing values. This screen is read-only."
    if len(pages) > 10:
        raise ValueError("This request exceeds the current limit of ten screens. Reduce the requested screens.")
