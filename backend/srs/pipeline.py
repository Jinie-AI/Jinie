"""
SRS Pipeline

Runs all SRS generation stages.

The original application description is passed into the sitemap stage
so that screen names are based on the actual application rather than
the grammar of generated functional requirements.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Optional

from common.schemas import (
    FullSRSOutput,
    PipelineTiming,
)

from .requirements_generator.requirement import (
    extract_raw_features,
)

from .fr_generator.functional import (
    generate_functional_requirements,
)

from .nfr_generator.non_functional import (
    generate_non_functional_requirements,
)

from .stack_identifier_generator.stack_identifier import (
    identify_tech_stack,
)

from .component_tree_generator.component_tree import (
    generate_component_trees,
)

from .sitemap_generator.sitemap import (
    generate_sitemap,
)

from .entities_generator.entities import (
    generate_entities,
)


logger = logging.getLogger(__name__)


# =========================================================
# ERROR
# =========================================================

class SRSPipelineError(Exception):
    pass


# =========================================================
# TRACE ID
# =========================================================

def _new_trace_id() -> str:

    return f"trc-{uuid.uuid4().hex[:12]}"


# =========================================================
# PROGRESS
# =========================================================

def _send_progress(
    progress_callback,
    progress,
    stage,
    message,
):

    if progress_callback:

        progress_callback(
            {
                "type": "progress",
                "progress": progress,
                "stage": stage,
                "message": message,
            }
        )


# =========================================================
# MAIN PIPELINE
# =========================================================

def run_srs_pipeline(
    prompt: str,
    trace_id: Optional[str] = None,
    progress_callback=None,
) -> FullSRSOutput:

    trace_id = (
        trace_id
        or _new_trace_id()
    )

    pipeline_start = time.perf_counter()

    stage_timings: list[
        PipelineTiming
    ] = []

    print()
    print("=" * 60)
    print("SRS PIPELINE START")
    print("TRACE ID:", trace_id)
    print("=" * 60)
    print()

    # =====================================================
    # STAGE 1 — REQUIREMENTS
    # =====================================================

    _send_progress(
        progress_callback,
        5,
        "requirements",
        "Analyzing your project requirements...",
    )

    print("STAGE 1: REQUIREMENTS")

    stage_start = time.perf_counter()

    try:

        raw_features = extract_raw_features(
            prompt,
            trace_id,
        )

        print("STAGE 1 COMPLETE")

    except Exception as exc:

        print(
            "STAGE 1 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 1 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 1 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="requirement",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # STAGE 2 — FUNCTIONAL REQUIREMENTS
    # =====================================================

    _send_progress(
        progress_callback,
        20,
        "functional",
        "Generating functional requirements...",
    )

    print("STAGE 2: FUNCTIONAL REQUIREMENTS")

    stage_start = time.perf_counter()

    try:

        functional_set = (
            generate_functional_requirements(
                raw_features,
                trace_id,
            )
        )

        print("STAGE 2 COMPLETE")

    except Exception as exc:

        print(
            "STAGE 2 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 2 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 2 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="functional",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # STAGE 3 — NON-FUNCTIONAL REQUIREMENTS
    # =====================================================

    _send_progress(
        progress_callback,
        35,
        "non_functional",
        "Generating non-functional requirements...",
    )

    print("STAGE 3: NON-FUNCTIONAL REQUIREMENTS")

    stage_start = time.perf_counter()

    try:

        non_functional_set = (
            generate_non_functional_requirements(
                functional_set,
                trace_id,
            )
        )

        print("STAGE 3 COMPLETE")

    except Exception as exc:

        print(
            "STAGE 3 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 3 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 3 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="non_functional",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # STAGE 4 — SITEMAP
    # =====================================================

    _send_progress(
        progress_callback,
        50,
        "sitemap",
        "Building application screens and navigation...",
    )

    print("STAGE 4: SITEMAP")

    stage_start = time.perf_counter()

    try:

        # IMPORTANT:
        #
        # We now pass the original normalized application
        # description into the sitemap generator.
        #
        # This is the main fix.

        sitemap = generate_sitemap(
            functional_set=functional_set,
            trace_id=trace_id,
            app_description=raw_features.normalized_text,
        )

        print(
            "STAGE 4 COMPLETE"
        )

        print(
            "SCREENS GENERATED:",
            len(sitemap.nodes),
        )

        for screen in sitemap.nodes:

            print(
                "  -",
                screen.screen_name,
                screen.route,
            )

    except Exception as exc:

        print(
            "STAGE 4 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 4 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 4 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="sitemap",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # STAGE 5 — ENTITIES
    # =====================================================

    _send_progress(
        progress_callback,
        65,
        "entities",
        "Identifying application data entities...",
    )

    print("STAGE 5: ENTITIES")

    stage_start = time.perf_counter()

    try:

        entity_set = generate_entities(
            raw_features,
            functional_set,
            trace_id,
        )

        print(
            "STAGE 5 COMPLETE"
        )

    except Exception as exc:

        print(
            "STAGE 5 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 5 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 5 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="entities",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # STAGE 6 — COMPONENT TREE
    # =====================================================

    _send_progress(
        progress_callback,
        80,
        "component_tree",
        "Building the component structure...",
    )

    print("STAGE 6: COMPONENT TREE")

    stage_start = time.perf_counter()

    try:

        component_tree_set = (
            generate_component_trees(
                sitemap,
                trace_id,
                functional_set=functional_set,
                app_description=(
                    raw_features.normalized_text
                ),
            )
        )

        print(
            "STAGE 6 COMPLETE"
        )

    except Exception as exc:

        print(
            "STAGE 6 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 6 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 6 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="component_tree",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # STAGE 7 — TECH STACK
    # =====================================================

    _send_progress(
        progress_callback,
        95,
        "tech_stack",
        "Selecting the recommended technology stack...",
    )

    print("STAGE 7: TECH STACK")

    stage_start = time.perf_counter()

    try:

        tech_stack = identify_tech_stack(
            functional_set,
            non_functional_set,
            entity_set,
            trace_id,
        )

        print(
            "STAGE 7 COMPLETE"
        )

    except Exception as exc:

        print(
            "STAGE 7 ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Stage 7 failed",
            trace_id,
        )

        raise SRSPipelineError(
            f"Stage 7 failed: {exc}"
        ) from exc

    stage_timings.append(
        PipelineTiming(
            stage_name="stack_identifier",
            duration_ms=(
                time.perf_counter()
                - stage_start
            ) * 1000,
        )
    )

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    total_duration_ms = (
        time.perf_counter()
        - pipeline_start
    ) * 1000

    print()
    print(
        "ASSEMBLING FINAL SRS OUTPUT..."
    )

    try:

        output = FullSRSOutput(
            trace_id=trace_id,
            raw_features=raw_features,
            functional_requirements=functional_set,
            non_functional_requirements=(
                non_functional_set
            ),
            sitemap=sitemap,
            entities=entity_set,
            component_trees=component_tree_set,
            tech_stack=tech_stack,
            stage_timings=stage_timings,
            total_duration_ms=(
                total_duration_ms
            ),
        )

    except Exception as exc:

        print(
            "FINAL OUTPUT ERROR:",
            exc,
        )

        logger.exception(
            "trace_id=%s | Failed to assemble final output",
            trace_id,
        )

        raise SRSPipelineError(
            f"Failed to assemble final SRS output: {exc}"
        ) from exc

    # =====================================================
    # COMPLETE
    # =====================================================

    _send_progress(
        progress_callback,
        100,
        "complete",
        "SRS generation complete!",
    )

    print()
    print("=" * 60)
    print("SRS PIPELINE COMPLETE")
    print(
        "TOTAL TIME:",
        round(
            total_duration_ms,
            2,
        ),
        "ms",
    )
    print("=" * 60)
    print()

    return output