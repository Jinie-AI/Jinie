"""
functional.py

Stage 2 of the SRS pipeline. Converts RawRequirementFeatures into a
set of atomic Functional Requirements (FRs), each with a stable
fr_id, actors, inputs, and outputs.

Primary path: calls the LLM (via models/functional_model.py) to
generate FRs directly from the app description, so it can handle any
app idea, not just pre-anticipated categories.

Fallback path: if the LLM call fails for any reason, this module maps
intent tags and keywords onto known functional archetypes (auth, feed,
ecommerce, etc) using fixed templates. Each archetype expansion is
wrapped in its own try/except so a failure generating one FR doesn't
take down the whole set.
"""

from __future__ import annotations

import logging
import time
from typing import List

from common.schemas import (
    RawRequirementFeatures,
    FunctionalRequirement,
    FunctionalRequirementSet,
    Priority,
)
from fr_generator.functional_model import generate_frs_with_llm

logger = logging.getLogger(__name__)

_VALID_PRIORITIES = {"critical", "high", "medium", "low"}


# ---------------------------------------------------------------------
# Archetype expansion table: intent -> list of FR templates
# ---------------------------------------------------------------------

_FR_ARCHETYPES = {
    "auth": [
        {
            "description": "User registers a new account using email/phone and password.",
            "actors": ["Guest"],
            "inputs": ["email_or_phone", "password", "confirm_password"],
            "outputs": ["account_created_confirmation", "auth_token"],
            "priority": Priority.CRITICAL,
        },
        {
            "description": "User logs into an existing account with valid credentials.",
            "actors": ["RegisteredUser"],
            "inputs": ["email_or_phone", "password"],
            "outputs": ["auth_token", "user_session"],
            "priority": Priority.CRITICAL,
        },
    ],
    "social_feed": [
        {
            "description": "User views a paginated feed of posts from followed accounts.",
            "actors": ["AuthenticatedUser"],
            "inputs": ["pagination_cursor"],
            "outputs": ["feed_items_list"],
            "priority": Priority.HIGH,
        },
        {
            "description": "User creates a new post with text and/or media.",
            "actors": ["AuthenticatedUser"],
            "inputs": ["post_text", "post_media"],
            "outputs": ["created_post_object"],
            "priority": Priority.HIGH,
        },
    ],
    "ecommerce": [
        {
            "description": "User browses a catalog of products with filtering.",
            "actors": ["AuthenticatedUser", "Guest"],
            "inputs": ["category_filter", "search_query"],
            "outputs": ["product_list"],
            "priority": Priority.HIGH,
        },
        {
            "description": "User adds a product to the shopping cart and checks out.",
            "actors": ["AuthenticatedUser"],
            "inputs": ["product_id", "quantity", "payment_method"],
            "outputs": ["order_confirmation"],
            "priority": Priority.CRITICAL,
        },
    ],
    "messaging": [
        {
            "description": "User sends and receives real-time messages with another user.",
            "actors": ["AuthenticatedUser"],
            "inputs": ["recipient_id", "message_text"],
            "outputs": ["message_delivered_status"],
            "priority": Priority.HIGH,
        },
    ],
    "profile": [
        {
            "description": "User views and edits their own profile information.",
            "actors": ["AuthenticatedUser"],
            "inputs": ["display_name", "avatar_image", "bio"],
            "outputs": ["updated_profile_object"],
            "priority": Priority.MEDIUM,
        },
    ],
    "dashboard": [
        {
            "description": "User views aggregated analytics/metrics on a dashboard view.",
            "actors": ["AuthenticatedUser"],
            "inputs": ["date_range_filter"],
            "outputs": ["aggregated_metrics"],
            "priority": Priority.MEDIUM,
        },
    ],
}

_DEFAULT_FR_TEMPLATE = {
    "description": "User interacts with the core application flow described in the prompt.",
    "actors": ["AuthenticatedUser"],
    "inputs": ["user_input"],
    "outputs": ["application_response"],
    "priority": Priority.MEDIUM,
}


def _build_fr_id(index: int) -> str:
    return f"FR-{index:03d}"


def _generate_via_templates(
    raw_features: RawRequirementFeatures, trace_id: str
) -> List[FunctionalRequirement]:
    """Fallback path: fixed archetype/template expansion (deterministic, offline)."""
    requirements: List[FunctionalRequirement] = []
    fr_counter = 1
    intents_to_expand = raw_features.intent_tags or ["default"]

    for intent in intents_to_expand:
        templates = _FR_ARCHETYPES.get(intent, [_DEFAULT_FR_TEMPLATE] if intent == "default" else [])
        if not templates:
            logger.debug("trace_id=%s | functional.py | no archetype found for intent=%s, skipping", trace_id, intent)
            continue

        for template in templates:
            try:
                fr = FunctionalRequirement(
                    fr_id=_build_fr_id(fr_counter),
                    description=template["description"],
                    actors=template["actors"],
                    inputs=template["inputs"],
                    outputs=template["outputs"],
                    priority=template["priority"],
                    source_keywords=[kw for kw in raw_features.extracted_keywords if kw in template["description"].lower()],
                )
                requirements.append(fr)
                fr_counter += 1
                logger.debug("trace_id=%s | functional.py | generated %s from intent=%s", trace_id, fr.fr_id, intent)
            except Exception as exc:  # noqa: BLE001
                logger.critical(
                    "trace_id=%s | functional.py | failed to build FR from intent=%s | error=%s",
                    trace_id, intent, str(exc), exc_info=True,
                )
                continue  # isolated failure, do not crash the whole set

    if not requirements:
        logger.warning(
            "trace_id=%s | functional.py | no functional requirements generated via templates, using default",
            trace_id,
        )
        try:
            requirements.append(
                FunctionalRequirement(
                    fr_id=_build_fr_id(1),
                    description=_DEFAULT_FR_TEMPLATE["description"],
                    actors=_DEFAULT_FR_TEMPLATE["actors"],
                    inputs=_DEFAULT_FR_TEMPLATE["inputs"],
                    outputs=_DEFAULT_FR_TEMPLATE["outputs"],
                    priority=_DEFAULT_FR_TEMPLATE["priority"],
                    source_keywords=[],
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.critical("trace_id=%s | functional.py | fallback FR construction also failed | error=%s", trace_id, str(exc), exc_info=True)

    return requirements


def generate_functional_requirements(
    raw_features: RawRequirementFeatures, trace_id: str
) -> FunctionalRequirementSet:
    """
    Entry point for Stage 2. Tries the LLM first (generate_frs_with_llm),
    which can handle any app description, not just pre-anticipated
    categories. Falls back to fixed archetype/template expansion if the
    LLM call fails or returns nothing usable.
    """
    start_time = time.perf_counter()
    logger.info(
        "trace_id=%s | functional.py | stage=start | intents=%s",
        trace_id, raw_features.intent_tags,
    )

    requirements: List[FunctionalRequirement] = []

    llm_frs = generate_frs_with_llm(
        raw_features.normalized_text, raw_features.extracted_keywords, raw_features.intent_tags, trace_id
    )

    if llm_frs is not None:
        logger.info("trace_id=%s | functional.py | using LLM-generated FRs (model path)", trace_id)
        for index, item in enumerate(llm_frs, start=1):
            try:
                priority_str = item["priority"] if item["priority"] in _VALID_PRIORITIES else "medium"
                fr = FunctionalRequirement(
                    fr_id=_build_fr_id(index),
                    description=item["description"],
                    actors=item["actors"],
                    inputs=item["inputs"],
                    outputs=item["outputs"],
                    priority=Priority(priority_str),
                    source_keywords=[kw for kw in raw_features.extracted_keywords if kw in item["description"].lower()],
                )
                requirements.append(fr)
            except Exception as exc:  # noqa: BLE001
                logger.critical(
                    "trace_id=%s | functional.py | failed to build FR object from LLM item at index=%d | error=%s",
                    trace_id, index, str(exc), exc_info=True,
                )
                continue  # isolated failure, skip just this one FR

    if not requirements:
        logger.warning(
            "trace_id=%s | functional.py | LLM path unavailable/empty, falling back to template archetypes",
            trace_id,
        )
        requirements = _generate_via_templates(raw_features, trace_id)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "trace_id=%s | functional.py | stage=complete | fr_count=%d duration_ms=%.2f",
        trace_id, len(requirements), elapsed_ms,
    )

    return FunctionalRequirementSet(trace_id=trace_id, requirements=requirements)