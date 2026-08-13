"""
pipeline.py

The transactional engine orchestrator for the srs/ module. Instantiates
and runs all seven processing stages in order, threading a single
trace_id through every stage's logs, timing each stage individually,
and assembling the final FullSRSOutput object.

This is the function the Engine Coordinator (backend/engine/) calls
for every incoming user prompt.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Optional
from common.schemas import FullSRSOutput, PipelineTiming

from .requirements_generator.requirement import extract_raw_features
from .fr_generator.functional import generate_functional_requirements
from .nfr_generator.non_functional import generate_non_functional_requirements
from .stack_identifier_generator.stack_identifier import identify_tech_stack
from .component_tree_generator.component_tree import generate_component_trees
from .sitemap_generator.sitemap import generate_sitemap
from .entities_generator.entities import generate_entities

logger = logging.getLogger(__name__)


class SRSPipelineError(Exception):
    """Raised only when the pipeline cannot produce any usable output at all."""


def _new_trace_id() -> str:
    return f"trc-{uuid.uuid4().hex[:12]}"


def run_srs_pipeline(prompt: str, trace_id: Optional[str] = None) -> FullSRSOutput:
    """
    Runs the full SRS generation pipeline against a raw user prompt and
    returns a single FullSRSOutput object. Each of the 7 stages tries
    its LLM path first and falls back to deterministic rules if the
    LLM call fails — no single stage failure crashes the pipeline.
    """
    trace_id = trace_id or _new_trace_id()
    pipeline_start = time.perf_counter()
    stage_timings: list[PipelineTiming] = []

    logger.info("trace_id=%s | pipeline.py | ===== SRS PIPELINE START =====", trace_id)

    stage_start = time.perf_counter()
    try:
        raw_features = extract_raw_features(prompt, trace_id)
    except Exception as exc:  # noqa: BLE001
        logger.critical(
            "trace_id=%s | pipeline.py | FATAL: Stage 1 (requirement extraction) raised unexpectedly | error=%s",
            trace_id, str(exc), exc_info=True,
        )
        raise SRSPipelineError(f"Stage 1 failed catastrophically for trace_id={trace_id}") from exc
    stage_timings.append(PipelineTiming(stage_name="requirement", duration_ms=(time.perf_counter() - stage_start) * 1000))

    stage_start = time.perf_counter()
    functional_set = generate_functional_requirements(raw_features, trace_id)
    stage_timings.append(PipelineTiming(stage_name="functional", duration_ms=(time.perf_counter() - stage_start) * 1000))

    stage_start = time.perf_counter()
    non_functional_set = generate_non_functional_requirements(functional_set, trace_id)
    stage_timings.append(PipelineTiming(stage_name="non_functional", duration_ms=(time.perf_counter() - stage_start) * 1000))

    stage_start = time.perf_counter()
    sitemap = generate_sitemap(functional_set, trace_id)
    stage_timings.append(PipelineTiming(stage_name="sitemap", duration_ms=(time.perf_counter() - stage_start) * 1000))

    stage_start = time.perf_counter()
    entity_set = generate_entities(raw_features, functional_set, trace_id)
    stage_timings.append(PipelineTiming(stage_name="entities", duration_ms=(time.perf_counter() - stage_start) * 1000))

    stage_start = time.perf_counter()
    component_tree_set = generate_component_trees(
        sitemap, trace_id, functional_set=functional_set,
        app_description=raw_features.normalized_text,
    )
    stage_timings.append(PipelineTiming(stage_name="component_tree", duration_ms=(time.perf_counter() - stage_start) * 1000))

    stage_start = time.perf_counter()
    tech_stack = identify_tech_stack(functional_set, non_functional_set, entity_set, trace_id)
    stage_timings.append(PipelineTiming(stage_name="stack_identifier", duration_ms=(time.perf_counter() - stage_start) * 1000))

    total_duration_ms = (time.perf_counter() - pipeline_start) * 1000

    try:
        output = FullSRSOutput(
            trace_id=trace_id,
            raw_features=raw_features,
            functional_requirements=functional_set,
            non_functional_requirements=non_functional_set,
            sitemap=sitemap,
            entities=entity_set,
            component_trees=component_tree_set,
            tech_stack=tech_stack,
            stage_timings=stage_timings,
            total_duration_ms=total_duration_ms,
        )
    except Exception as exc:  # noqa: BLE001
        logger.critical(
            "trace_id=%s | pipeline.py | FATAL: failed to assemble FullSRSOutput | error=%s",
            trace_id, str(exc), exc_info=True,
        )
        raise SRSPipelineError(f"Failed to assemble final SRS output for trace_id={trace_id}") from exc

    logger.info(
        "trace_id=%s | pipeline.py | ===== SRS PIPELINE COMPLETE ===== total_duration_ms=%.2f "
        "fr=%d nfr=%d screens=%d entities=%d trees=%d",
        trace_id, total_duration_ms, len(functional_set.requirements), len(non_functional_set.requirements),
        len(sitemap.nodes), len(entity_set.entities), len(component_tree_set.trees),
    )

    for timing in stage_timings:
        logger.debug("trace_id=%s | pipeline.py | stage_timing | %s=%.2fms", trace_id, timing.stage_name, timing.duration_ms)

    return output
