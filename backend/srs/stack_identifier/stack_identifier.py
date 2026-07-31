"""
stack_identifier.py

Stage 7 of the SRS pipeline. Determines the concrete framework and
library targets (React Native Expo, Zustand, Tamagui, Firestore, etc)
based on functional keywords, entity complexity, and non-functional
constraints gathered in earlier stages.

Primary path: calls the LLM (via stack_identifier_model.py) to pick
state management, UI library, and backend service with reasoning
tailored to the actual app, instead of relying only on fixed if/else
thresholds.

Fallback path: if the LLM call fails, uses the fixed rule-based
selection functions below (deterministic, offline).
"""

from __future__ import annotations

import logging
import time
from typing import List

from common.schemas import (
    FunctionalRequirementSet,
    NonFunctionalRequirementSet,
    EntitySet,
    TechStackSelection,
    NFRCategory,
)
from stack_identifier_generator.stack_identifier_model import identify_stack_with_llm
from logger import Logger

logger = logging.getLogger(__name__)

_BASE_FRAMEWORK = "React Native (Expo)"
_BASE_NAVIGATION = "React Navigation"


def _select_state_management(functional_set: FunctionalRequirementSet) -> tuple[str, str]:
    fr_count = len(functional_set.requirements)
    if fr_count <= 3:
        return "React Context + useReducer", "Small FR count; lightweight built-in state is sufficient."
    return "Zustand", "Moderate-to-large FR count; Zustand offers low-boilerplate global state without excessive Context nesting."


def _select_ui_library(functional_set: FunctionalRequirementSet) -> tuple[str, str]:
    haystack = " ".join(fr.description.lower() for fr in functional_set.requirements)
    if "chart" in haystack or "dashboard" in haystack or "metric" in haystack:
        return "Tamagui + Victory Native", "Dashboard/analytics content detected; Victory Native adds charting on top of Tamagui's design system."
    return "Tamagui", "Tamagui gives themeable, performant primitives suited for most generated screens."


def _select_backend_service(entity_set: EntitySet, functional_set: FunctionalRequirementSet) -> tuple[str, str]:
    haystack = " ".join(fr.description.lower() for fr in functional_set.requirements)
    if "payment" in haystack or "order_confirmation" in haystack:
        return "Firebase (Firestore + Cloud Functions + Stripe integration)", "Payment/order flows detected; Cloud Functions bridge secure payment processing."
    if len(entity_set.entities) > 6:
        return "Firebase Firestore (with composite indexes)", "High entity count benefits from Firestore's flexible document model with indexed queries."
    return "Firebase Firestore", "Default managed backend for rapid, serverless data persistence."


def _select_security_additions(non_functional_set: NonFunctionalRequirementSet) -> List[str]:
    reasons = []
    security_nfrs = [n for n in non_functional_set.requirements if n.category == NFRCategory.SECURITY]
    if security_nfrs:
        reasons.append(
            f"{len(security_nfrs)} security-category NFR(s) detected; Firebase Auth + App Check recommended for token/session integrity."
        )
    return reasons


def _identify_via_rules(
    functional_set: FunctionalRequirementSet,
    non_functional_set: NonFunctionalRequirementSet,
    entity_set: EntitySet,
    trace_id: str,
) -> TechStackSelection:
    """Fallback path: fixed if/else rule-based selection (deterministic, offline)."""
    reasoning: List[str] = []

    try:
        state_management, state_reason = _select_state_management(functional_set)
        reasoning.append(state_reason)
    except Exception as exc:  # noqa: BLE001
        logger.critical("trace_id=%s | stack_identifier.py | state management selection failed | error=%s", trace_id, str(exc), exc_info=True)
        state_management = "Zustand"
        reasoning.append("Fallback default applied due to selection error.")

    try:
        ui_library, ui_reason = _select_ui_library(functional_set)
        reasoning.append(ui_reason)
    except Exception as exc:  # noqa: BLE001
        logger.critical("trace_id=%s | stack_identifier.py | ui library selection failed | error=%s", trace_id, str(exc), exc_info=True)
        ui_library = "Tamagui"
        reasoning.append("Fallback default applied due to selection error.")

    try:
        backend_service, backend_reason = _select_backend_service(entity_set, functional_set)
        reasoning.append(backend_reason)
    except Exception as exc:  # noqa: BLE001
        logger.critical("trace_id=%s | stack_identifier.py | backend service selection failed | error=%s", trace_id, str(exc), exc_info=True)
        backend_service = "Firebase Firestore"
        reasoning.append("Fallback default applied due to selection error.")

    try:
        reasoning.extend(_select_security_additions(non_functional_set))
    except Exception as exc:  # noqa: BLE001
        logger.critical("trace_id=%s | stack_identifier.py | security addition scan failed | error=%s", trace_id, str(exc), exc_info=True)

    return TechStackSelection(
        framework=_BASE_FRAMEWORK,
        state_management=state_management,
        ui_library=ui_library,
        navigation_library=_BASE_NAVIGATION,
        backend_service=backend_service,
        reasoning=reasoning,
    )


def identify_tech_stack(
    functional_set: FunctionalRequirementSet,
    non_functional_set: NonFunctionalRequirementSet,
    entity_set: EntitySet,
    trace_id: str,
) -> TechStackSelection:
    """
    Entry point for Stage 7. Tries the LLM first (identify_stack_with_llm),
    which tailors the stack choice and reasoning to the actual app.
    Falls back to fixed if/else rules if the LLM call fails or returns
    nothing usable.
    """
    start_time = time.perf_counter()
    logger_instance = Logger(trace_id=trace_id)
    logger_instance.log_event(
        "stack_identifier.py",
        f"Starting stack identification | fr_count={len(functional_set.requirements)} "
        f"nfr_count={len(non_functional_set.requirements)} entity_count={len(entity_set.entities)}",
    )
    logger.info(
        "trace_id=%s | stack_identifier.py | stage=start | fr_count=%d nfr_count=%d entity_count=%d",
        trace_id, len(functional_set.requirements), len(non_functional_set.requirements), len(entity_set.entities),
    )

    fr_summaries = [{"fr_id": fr.fr_id, "description": fr.description, "priority": fr.priority.value} for fr in functional_set.requirements]
    nfr_summaries = [{"category": n.category.value, "constraint": n.constraint} for n in non_functional_set.requirements]

    llm_result = identify_stack_with_llm(fr_summaries, nfr_summaries, len(entity_set.entities), trace_id)

    if llm_result is not None:
        logger_instance.log_event("stack_identifier.py", "Using LLM-selected stack (model path)")
        logger.info("trace_id=%s | stack_identifier.py | using LLM-selected stack (model path)", trace_id)
        try:
            selection = TechStackSelection(
                framework=_BASE_FRAMEWORK,
                state_management=llm_result["state_management"],
                ui_library=llm_result["ui_library"],
                navigation_library=_BASE_NAVIGATION,
                backend_service=llm_result["backend_service"],
                reasoning=llm_result["reasoning"],
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger_instance.log_event(
                "stack_identifier.py",
                f"Stage complete | state={selection.state_management} ui={selection.ui_library} "
                f"backend={selection.backend_service} duration_ms={elapsed_ms:.2f}",
            )
            logger.info(
                "trace_id=%s | stack_identifier.py | stage=complete | state=%s ui=%s backend=%s duration_ms=%.2f",
                trace_id, selection.state_management, selection.ui_library, selection.backend_service, elapsed_ms,
            )
            return selection
        except Exception as exc:  # noqa: BLE001
            logger_instance.log_event("stack_identifier.py", f"Failed to build TechStackSelection from LLM result | error={str(exc)}", level="CRITICAL")
            logger.critical(
                "trace_id=%s | stack_identifier.py | failed to build TechStackSelection from LLM result | error=%s",
                trace_id, str(exc), exc_info=True,
            )
            # fall through to rules below

    logger_instance.log_event("stack_identifier.py", "LLM path unavailable/failed, falling back to rule-based selection", level="WARNING")
    logger.warning(
        "trace_id=%s | stack_identifier.py | LLM path unavailable/failed, falling back to rule-based selection",
        trace_id,
    )
    selection = _identify_via_rules(functional_set, non_functional_set, entity_set, trace_id)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger_instance.log_event(
        "stack_identifier.py",
        f"Stage complete | state={selection.state_management} ui={selection.ui_library} "
        f"backend={selection.backend_service} duration_ms={elapsed_ms:.2f}",
    )
    logger.info(
        "trace_id=%s | stack_identifier.py | stage=complete | state=%s ui=%s backend=%s duration_ms=%.2f",
        trace_id, selection.state_management, selection.ui_library, selection.backend_service, elapsed_ms,
    )

    return selection