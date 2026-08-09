"""
non_functional.py

Stage 3 of the SRS pipeline. Evaluates the generated Functional
Requirements and injects Non-Functional Requirements (NFRs) —
performance envelopes, security bounds, reliability/usability
constraints — each linked back to the fr_id it governs.

Primary path: calls the LLM (via models/non_functional_model.py) to
generate NFRs tailored to the actual FR list, so constraints aren't
limited to a fixed keyword-trigger table.

Fallback path: if the LLM call fails, applies baseline constraints to
every FR plus keyword-triggered constraints from a fixed table.
"""

from __future__ import annotations

import logging
import time
from typing import List

from common.schemas import (
    FunctionalRequirementSet,
    NonFunctionalRequirement,
    NonFunctionalRequirementSet,
    NFRCategory,
    Priority,
)
from .non_functional_model import generate_nfrs_with_llm
from logger import Logger

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Baseline constraints applied to every FR regardless of content
# ---------------------------------------------------------------------

_BASELINE_CONSTRAINTS = [
    {
        "category": NFRCategory.PERFORMANCE,
        "constraint": "Screen render must complete within 200ms of navigation trigger.",
        "threshold_value": 200.0,
        "threshold_unit": "ms",
    },
    {
        "category": NFRCategory.RELIABILITY,
        "constraint": "Operation must degrade gracefully with a retry-capable error state on failure.",
        "threshold_value": None,
        "threshold_unit": None,
    },
]

# ---------------------------------------------------------------------
# Content-triggered constraints: keyword found in FR description/inputs
# -> additional NFR category injected
# ---------------------------------------------------------------------

_TRIGGERED_CONSTRAINTS = {
    "password": {
        "category": NFRCategory.SECURITY,
        "constraint": "Credentials must be transmitted over TLS and never logged in plaintext.",
        "threshold_value": None,
        "threshold_unit": None,
    },
    "payment": {
        "category": NFRCategory.SECURITY,
        "constraint": "Payment data must be handled via PCI-DSS compliant tokenization, never stored raw.",
        "threshold_value": None,
        "threshold_unit": None,
    },
    "auth_token": {
        "category": NFRCategory.SECURITY,
        "constraint": "Auth tokens must expire and be refreshed using short-lived rotation.",
        "threshold_value": 3600.0,
        "threshold_unit": "s",
    },
    "feed_items_list": {
        "category": NFRCategory.SCALABILITY,
        "constraint": "Feed pagination must support incremental loading without full re-fetch.",
        "threshold_value": 20.0,
        "threshold_unit": "items_per_page",
    },
    "message_text": {
        "category": NFRCategory.PERFORMANCE,
        "constraint": "Message delivery round-trip must complete within 500ms under normal network conditions.",
        "threshold_value": 500.0,
        "threshold_unit": "ms",
    },
}


def _build_nfr_id(index: int) -> str:
    return f"NFR-{index:03d}"


def _generate_via_rules(
    functional_set: FunctionalRequirementSet, trace_id: str
) -> List[NonFunctionalRequirement]:
    """Fallback path: fixed baseline + keyword-triggered constraints (deterministic, offline)."""
    nfrs: List[NonFunctionalRequirement] = []
    nfr_counter = 1

    for fr in functional_set.requirements:
        try:
            for baseline in _BASELINE_CONSTRAINTS:
                nfr = NonFunctionalRequirement(
                    nfr_id=_build_nfr_id(nfr_counter),
                    category=baseline["category"],
                    constraint=baseline["constraint"],
                    linked_fr_id=fr.fr_id,
                    threshold_value=baseline["threshold_value"],
                    threshold_unit=baseline["threshold_unit"],
                )
                nfrs.append(nfr)
                nfr_counter += 1
        except Exception as exc:  # noqa: BLE001
            logger.critical(
                "trace_id=%s | non_functional.py | baseline injection failed for fr_id=%s | error=%s",
                trace_id, fr.fr_id, str(exc), exc_info=True,
            )
            continue

        haystack = " ".join([fr.description.lower(), *[i.lower() for i in fr.inputs], *[o.lower() for o in fr.outputs]])
        for trigger_keyword, template in _TRIGGERED_CONSTRAINTS.items():
            if trigger_keyword.lower() in haystack:
                try:
                    nfr = NonFunctionalRequirement(
                        nfr_id=_build_nfr_id(nfr_counter),
                        category=template["category"],
                        constraint=template["constraint"],
                        linked_fr_id=fr.fr_id,
                        threshold_value=template["threshold_value"],
                        threshold_unit=template["threshold_unit"],
                    )
                    nfrs.append(nfr)
                    nfr_counter += 1
                    logger.debug(
                        "trace_id=%s | non_functional.py | triggered constraint '%s' matched on fr_id=%s",
                        trace_id, trigger_keyword, fr.fr_id,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.critical(
                        "trace_id=%s | non_functional.py | triggered constraint injection failed for fr_id=%s trigger=%s | error=%s",
                        trace_id, fr.fr_id, trigger_keyword, str(exc), exc_info=True,
                    )
                    continue

    return nfrs


def generate_non_functional_requirements(
    functional_set: FunctionalRequirementSet, trace_id: str
) -> NonFunctionalRequirementSet:
    """
    Entry point for Stage 3. Tries the LLM first (generate_nfrs_with_llm),
    which tailors constraints to the actual FR list rather than a fixed
    keyword table. Falls back to rule-based baseline + triggered
    constraints if the LLM call fails or returns nothing usable.
    """
    start_time = time.perf_counter()
    logger_instance = Logger(trace_id=trace_id)
    logger_instance.log_event("non_functional.py", f"Starting NFR generation | fr_count={len(functional_set.requirements)}")
    logger.info(
        "trace_id=%s | non_functional.py | stage=start | fr_count=%d",
        trace_id, len(functional_set.requirements),
    )

    nfrs: List[NonFunctionalRequirement] = []

    fr_summaries = [
        {"fr_id": fr.fr_id, "description": fr.description, "priority": fr.priority.value}
        for fr in functional_set.requirements
    ]
    llm_nfrs = generate_nfrs_with_llm(fr_summaries, trace_id)

    if llm_nfrs is not None:
        logger_instance.log_event("non_functional.py", "Using LLM-generated NFRs (model path)")
        logger.info("trace_id=%s | non_functional.py | using LLM-generated NFRs (model path)", trace_id)
        for index, item in enumerate(llm_nfrs, start=1):
            try:
                nfr = NonFunctionalRequirement(
                    nfr_id=_build_nfr_id(index),
                    category=NFRCategory(item["category"]),
                    constraint=item["constraint"],
                    linked_fr_id=item["linked_fr_id"],
                    threshold_value=item["threshold_value"],
                    threshold_unit=item["threshold_unit"],
                )
                nfrs.append(nfr)
            except Exception as exc:  # noqa: BLE001
                logger_instance.log_event("non_functional.py", f"Failed to build NFR from LLM item at index={index} | error={str(exc)}", level="CRITICAL")
                logger.critical(
                    "trace_id=%s | non_functional.py | failed to build NFR object from LLM item at index=%d | error=%s",
                    trace_id, index, str(exc), exc_info=True,
                )
                continue  # isolated failure, skip just this one NFR

    if not nfrs:
        logger_instance.log_event("non_functional.py", "LLM path unavailable/empty, falling back to rule-based constraints", level="WARNING")
        logger.warning(
            "trace_id=%s | non_functional.py | LLM path unavailable/empty, falling back to rule-based constraints",
            trace_id,
        )
        nfrs = _generate_via_rules(functional_set, trace_id)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger_instance.log_event("non_functional.py", f"Stage complete | nfr_count={len(nfrs)} duration_ms={elapsed_ms:.2f}")
    logger.info(
        "trace_id=%s | non_functional.py | stage=complete | nfr_count=%d duration_ms=%.2f",
        trace_id, len(nfrs), elapsed_ms,
    )

    return NonFunctionalRequirementSet(trace_id=trace_id, requirements=nfrs)