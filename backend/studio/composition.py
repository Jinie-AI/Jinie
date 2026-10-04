"""Validated, serializable screen composition; no model-supplied executable code."""
from typing import Literal
import re
from pydantic import BaseModel, ConfigDict, Field

class Block(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["hero", "search", "categories", "collection", "spotlight", "statement"]
    title: str = Field(default="", max_length=100)
    body: str = Field(default="", max_length=240)
    layout: Literal["grid", "cards", "editorial", "rail", "mosaic"] = "grid"
    reference_component: str = Field(default="", max_length=160)

class Composition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal[1] = 1
    rationale: str = Field(default="", max_length=400)
    hero_style: Literal["image", "split", "typographic"] = "typographic"
    card_style: Literal["elevated", "outlined", "flat"] = "outlined"
    image_ratio: Literal["portrait", "square", "landscape"] = "square"
    density: Literal["airy", "balanced", "compact"] = "balanced"
    corners: Literal["sharp", "soft", "round"] = "soft"
    category_style: Literal["chips", "tiles"] = "chips"
    blocks: list[Block] = Field(min_length=1, max_length=8)


def requested_layout(prompt):
    text = prompt.casefold()
    for layout, phrases in (
        ("rail", ("carousel", "horizontal collection", "horizontal rail")),
        ("mosaic", ("mosaic", "asymmetric", "lookbook")),
        ("cards", ("compact menu", "menu rows", "list layout")),
    ):
        for phrase in phrases:
            if phrase in text and not re.search(
                r"\b(?:no|without|avoid|exclude|remove|do not use|don't use)\s+(?:a |an |the )?" + re.escape(phrase), text
            ):
                return layout
    return None

def default_composition(business, page, layout="grid", prompt=""):
    # Honest deterministic fallback for local-only planning and legacy projects.
    editorial = business in ("flowers", "furniture", "jewellery", "jewelry")
    menu = business in ("restaurant", "food", "bakery")
    kinds = (["hero", "spotlight", "categories", "collection"] if editorial else
             ["search", "categories", "collection", "statement"] if menu else
             ["hero", "search", "categories", "collection"])
    if page != "home": kinds = ["search", "categories", "collection"]
    text = prompt.casefold()
    layout = requested_layout(prompt) or layout
    if "category-first" in text or "categories first" in text:
        kinds = ["categories", "search", "collection", "hero"] if page == "home" else ["categories", "search", "collection"]
    return Composition(hero_style="image" if editorial else "split" if menu else "typographic",
        category_style="tiles" if "category tiles" in text else "chips",
        image_ratio="portrait" if editorial else "landscape" if menu else "square",
        density="airy" if editorial else "compact" if menu else "balanced",
        card_style="flat" if editorial else "outlined",
        rationale="Domain-based local composition. Refine the brief for a custom planned arrangement.",
        blocks=[Block(kind=kind, layout="cards" if menu and layout=="grid" else layout,
            title="Explore the collection" if kind=="collection" else "A closer look" if kind=="spotlight" else "Made for your everyday" if kind=="statement" else "") for kind in kinds]).model_dump()

def ground_composition(value, references, prompt=""):
    plan=Composition.model_validate(value).model_dump()
    known={item["name"] for item in references}
    for block in plan["blocks"]:
        if block["reference_component"] not in known:
            block["reference_component"]=""
    if not any(block["kind"]=="collection" for block in plan["blocks"]):
        block=Block(kind="collection",title="Explore the collection").model_dump()
        plan["blocks"]=(plan["blocks"][:7]+[block])
    text = prompt.casefold()
    requested = requested_layout(prompt)
    if requested:
        for block in plan["blocks"]:
            if block["kind"] == "collection":
                block["layout"] = requested
    if "category tiles" in text:
        plan["category_style"] = "tiles"
    return plan
