"""Validated, serializable screen composition; no model-supplied executable code."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Block(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["hero", "search", "categories", "collection", "spotlight", "statement"]
    title: str = Field(default="", max_length=100)
    body: str = Field(default="", max_length=240)
    layout: Literal["grid", "cards", "editorial"] = "grid"
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
    blocks: list[Block] = Field(min_length=1, max_length=8)

def default_composition(business, page, layout="grid"):
    # Honest deterministic fallback for local-only planning and legacy projects.
    editorial = business in ("flowers", "furniture", "jewelry")
    menu = business in ("restaurant", "food", "bakery")
    kinds = (["hero", "spotlight", "categories", "collection"] if editorial else
             ["search", "categories", "collection", "statement"] if menu else
             ["hero", "search", "categories", "collection"])
    if page != "home": kinds = ["search", "categories", "collection"]
    return Composition(hero_style="image" if editorial else "split" if menu else "typographic",
        image_ratio="portrait" if editorial else "landscape" if menu else "square",
        density="airy" if editorial else "compact" if menu else "balanced",
        card_style="flat" if editorial else "outlined",
        rationale="Domain-based local composition. Refine the brief for a custom planned arrangement.",
        blocks=[Block(kind=kind, layout="cards" if menu else layout,
            title="Explore the collection" if kind=="collection" else "A closer look" if kind=="spotlight" else "Made for your everyday" if kind=="statement" else "") for kind in kinds]).model_dump()

def ground_composition(value, references):
    plan=Composition.model_validate(value).model_dump()
    known={item["name"] for item in references}
    for block in plan["blocks"]:
        if block["reference_component"] not in known:
            block["reference_component"]=""
    if not any(block["kind"]=="collection" for block in plan["blocks"]):
        block=Block(kind="collection",title="Explore the collection").model_dump()
        plan["blocks"]=(plan["blocks"][:7]+[block])
    return plan
