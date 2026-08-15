"""
router.py

FastAPI router exposing Stage 5 (Component Generator) as an HTTP
endpoint. This is the "new door" between the running app and the
already-built, already-tested ComponentGenerator: given the
component_trees produced by the SRS pipeline (Stage 6, see
srs/component_tree_generator/) and the design tokens the user picked
in the Design Preferences Panel, it returns real generated React
Native component source — one component per screen tree.

Import note: generator.py (and its siblings generator_model.py,
generator_validator.py, exceptions.py) use flat imports
(`from exceptions import ...`) rather than package-relative ones,
the same way component_generator/tests.py runs them directly from
inside this folder. To keep that working when this module is instead
imported normally as `component_generator.router` from main.py, this
folder is added to sys.path before anything from it is imported.
"""

from __future__ import annotations

import os
import sys
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from generator import ComponentGenerator  # noqa: E402
from exceptions import ComponentGenerationError  # noqa: E402

router = APIRouter(prefix="/api/components", tags=["components"])

# One shared generator instance — ComponentGenerator itself holds no
# per-request state, it just wraps the AI-first + rule-based-fallback
# logic, so reusing it across requests is safe.
_generator = ComponentGenerator()


# =====================================================================
# Request / response contracts
# =====================================================================

class ComponentTreeIn(BaseModel):
    """Mirrors common.schemas.ComponentTree, but accepts `root` as a
    raw dict instead of a strict ComponentNode model. The frontend
    sends whatever JSON the SRS pipeline gave it back verbatim — we
    don't need to re-validate the full recursive node shape here,
    ComponentGenerator's own _validate_layout_spec() already does
    that walk before anything is sent to the LLM."""

    model_config = ConfigDict(extra="allow")

    screen_id: str
    screen_name: str
    root: Dict[str, Any]


class GenerateComponentsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: Optional[str] = Field(
        default=None,
        description="Reuse the SRS pipeline's trace_id if you have it, for log correlation.",
    )
    component_trees: List[ComponentTreeIn] = Field(default_factory=list)
    design_tokens: Dict[str, Any] = Field(default_factory=dict)
    tech_stack: Optional[Dict[str, Any]] = None


class GeneratedComponent(BaseModel):
    screen_id: str
    screen_name: str
    component_name: str
    code: str
    layout: Dict[str, Any]


class FailedComponent(BaseModel):
    screen_id: str
    screen_name: str
    error: str


class GenerateComponentsResponse(BaseModel):
    trace_id: str
    components: List[GeneratedComponent]
    failed: List[FailedComponent] = Field(default_factory=list)


def _new_trace_id() -> str:
    return f"trc-{uuid.uuid4().hex[:12]}"


def _safe_component_name(screen_name: str) -> str:
    """ComponentGenerator requires an identifier-like name starting
    with a letter. Sitemap-generated screen_names are already
    PascalCase (e.g. 'ProductCatalog'), but this strips whitespace
    defensively in case a screen_name ever contains spaces."""
    return "".join(part.capitalize() if not part[:1].isupper() else part for part in screen_name.split())


# =====================================================================
# Endpoint
# =====================================================================

@router.post("/generate", response_model=GenerateComponentsResponse)
def generate_components(request: GenerateComponentsRequest) -> GenerateComponentsResponse:
    """
    Stage 5 entry point over HTTP. For each screen's component_tree,
    calls ComponentGenerator.generate_component() with the shared
    design_tokens (and tech_stack, if provided). One tree failing
    validation doesn't fail the whole request — it's reported in
    `failed` and generation continues for the rest.
    """
    if not request.component_trees:
        raise HTTPException(status_code=400, detail="component_trees must not be empty")

    trace_id = request.trace_id or _new_trace_id()

    generated: List[GeneratedComponent] = []
    failed: List[FailedComponent] = []

    for tree in request.component_trees:
        component_name = _safe_component_name(tree.screen_name) or tree.screen_id
        try:
            code = _generator.generate_component(
                component_name=component_name,
                design_tokens=request.design_tokens,
                layout_spec=tree.root,
                tech_stack=request.tech_stack,
                trace_id=trace_id,
            )
            generated.append(
                GeneratedComponent(
                    screen_id=tree.screen_id,
                    screen_name=tree.screen_name,
                    component_name=component_name,
                    code=code,
                    layout=tree.root,
                )
            )
        except ComponentGenerationError as exc:
            failed.append(
                FailedComponent(
                    screen_id=tree.screen_id,
                    screen_name=tree.screen_name,
                    error=str(exc),
                )
            )
        except Exception as exc:  # noqa: BLE001 — never let one bad tree 500 the whole batch
            failed.append(
                FailedComponent(
                    screen_id=tree.screen_id,
                    screen_name=tree.screen_name,
                    error=f"Unexpected error: {exc}",
                )
            )

    if not generated:
        raise HTTPException(
            status_code=500,
            detail=f"Component generation failed for every screen: {[f.model_dump() for f in failed]}",
        )

    return GenerateComponentsResponse(trace_id=trace_id, components=generated, failed=failed)
