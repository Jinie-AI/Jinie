"""
entities.py

Stage 5 of the SRS pipeline. Identifies core persistable data objects
(entities), their attributes/types, and entity-relationship mappings.

Primary path: calls the LLM (via entities_model.py) to identify
entities directly from the app description and FR list, so it isn't
limited to a pre-registered dictionary of known entity types.

Fallback path: if the LLM call fails, uses candidate_entities from
Stage 1 cross-referenced against a fixed entity archetype dictionary
(deterministic, offline).
"""

from __future__ import annotations

import logging
import time
from typing import List, Dict

from common.schemas import (
    RawRequirementFeatures,
    FunctionalRequirementSet,
    Entity,
    EntitySet,
    EntityAttribute,
    EntityRelationship,
    AttributeType,
    RelationshipType,
)
from .entities_model import generate_entities_with_llm
from logger import Logger

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Known entity archetypes: entity_name -> (attributes, relationships)
# ---------------------------------------------------------------------

_ENTITY_ARCHETYPES: Dict[str, Dict] = {
    "user": {
        "attributes": [
            ("user_id", AttributeType.STRING, True),
            ("email", AttributeType.STRING, True),
            ("display_name", AttributeType.STRING, False),
            ("avatar_url", AttributeType.STRING, False),
            ("created_at", AttributeType.TIMESTAMP, True),
        ],
        "relationships": [],
    },
    "post": {
        "attributes": [
            ("post_id", AttributeType.STRING, True),
            ("author_id", AttributeType.REFERENCE, True),
            ("content", AttributeType.STRING, True),
            ("media_urls", AttributeType.ARRAY, False),
            ("created_at", AttributeType.TIMESTAMP, True),
        ],
        "relationships": [("user", RelationshipType.ONE_TO_MANY)],
    },
    "comment": {
        "attributes": [
            ("comment_id", AttributeType.STRING, True),
            ("post_id", AttributeType.REFERENCE, True),
            ("author_id", AttributeType.REFERENCE, True),
            ("text", AttributeType.STRING, True),
        ],
        "relationships": [("post", RelationshipType.ONE_TO_MANY), ("user", RelationshipType.ONE_TO_MANY)],
    },
    "product": {
        "attributes": [
            ("product_id", AttributeType.STRING, True),
            ("name", AttributeType.STRING, True),
            ("price", AttributeType.NUMBER, True),
            ("stock_quantity", AttributeType.NUMBER, True),
            ("category", AttributeType.STRING, False),
        ],
        "relationships": [],
    },
    "order": {
        "attributes": [
            ("order_id", AttributeType.STRING, True),
            ("user_id", AttributeType.REFERENCE, True),
            ("total_amount", AttributeType.NUMBER, True),
            ("status", AttributeType.STRING, True),
            ("created_at", AttributeType.TIMESTAMP, True),
        ],
        "relationships": [("user", RelationshipType.ONE_TO_MANY), ("product", RelationshipType.MANY_TO_MANY)],
    },
    "message": {
        "attributes": [
            ("message_id", AttributeType.STRING, True),
            ("sender_id", AttributeType.REFERENCE, True),
            ("recipient_id", AttributeType.REFERENCE, True),
            ("text", AttributeType.STRING, True),
            ("sent_at", AttributeType.TIMESTAMP, True),
        ],
        "relationships": [("user", RelationshipType.MANY_TO_MANY)],
    },
    "notification": {
        "attributes": [
            ("notification_id", AttributeType.STRING, True),
            ("user_id", AttributeType.REFERENCE, True),
            ("type", AttributeType.STRING, True),
            ("read", AttributeType.BOOLEAN, True),
        ],
        "relationships": [("user", RelationshipType.ONE_TO_MANY)],
    },
    "review": {
        "attributes": [
            ("review_id", AttributeType.STRING, True),
            ("product_id", AttributeType.REFERENCE, True),
            ("user_id", AttributeType.REFERENCE, True),
            ("rating", AttributeType.NUMBER, True),
            ("text", AttributeType.STRING, False),
        ],
        "relationships": [("product", RelationshipType.ONE_TO_MANY), ("user", RelationshipType.ONE_TO_MANY)],
    },
    "cart": {
        "attributes": [
            ("cart_id", AttributeType.STRING, True),
            ("user_id", AttributeType.REFERENCE, True),
            ("items", AttributeType.ARRAY, True),
        ],
        "relationships": [("user", RelationshipType.ONE_TO_ONE), ("product", RelationshipType.MANY_TO_MANY)],
    },
    "payment": {
        "attributes": [
            ("payment_id", AttributeType.STRING, True),
            ("order_id", AttributeType.REFERENCE, True),
            ("amount", AttributeType.NUMBER, True),
            ("method", AttributeType.STRING, True),
            ("status", AttributeType.STRING, True),
        ],
        "relationships": [("order", RelationshipType.ONE_TO_ONE)],
    },
}


def _build_entity_id(index: int) -> str:
    return f"ENT-{index:03d}"


def _generate_via_rules(
    raw_features: RawRequirementFeatures,
    functional_set: FunctionalRequirementSet,
    trace_id: str,
) -> List[Entity]:
    """Fallback path: candidate_entities + fixed archetype dictionary (deterministic, offline)."""
    candidate_names = set(raw_features.candidate_entities)
    if not candidate_names:
        logger.debug("trace_id=%s | entities.py | no candidate entities from Stage 1, scanning FR text", trace_id)
        for fr in functional_set.requirements:
            haystack = " ".join([fr.description.lower(), *[i.lower() for i in fr.inputs], *[o.lower() for o in fr.outputs]])
            for known_entity in _ENTITY_ARCHETYPES:
                if known_entity in haystack:
                    candidate_names.add(known_entity)

    entities: List[Entity] = []
    entity_counter = 1

    for entity_name in sorted(candidate_names):
        archetype = _ENTITY_ARCHETYPES.get(entity_name)
        if archetype is None:
            logger.debug("trace_id=%s | entities.py | no archetype registered for '%s', skipping", trace_id, entity_name)
            continue

        try:
            attributes = [
                EntityAttribute(name=name, type=attr_type, required=required)
                for name, attr_type, required in archetype["attributes"]
            ]
            relationships = [
                EntityRelationship(from_entity=entity_name, to_entity=target, relationship_type=rel_type)
                for target, rel_type in archetype["relationships"]
                if target in candidate_names
            ]
            source_fr_ids = [
                fr.fr_id for fr in functional_set.requirements
                if entity_name in " ".join([fr.description.lower(), *fr.inputs, *fr.outputs]).lower()
            ]

            entity = Entity(
                entity_id=_build_entity_id(entity_counter),
                name=entity_name,
                attributes=attributes,
                relationships=relationships,
                source_fr_ids=source_fr_ids,
            )
            entities.append(entity)
            entity_counter += 1
            logger.debug("trace_id=%s | entities.py | built entity=%s with %d attributes", trace_id, entity_name, len(attributes))

        except Exception as exc:  # noqa: BLE001
            logger.critical(
                "trace_id=%s | entities.py | failed to build entity='%s' | error=%s",
                trace_id, entity_name, str(exc), exc_info=True,
            )
            continue

    return entities


def generate_entities(
    raw_features: RawRequirementFeatures,
    functional_set: FunctionalRequirementSet,
    trace_id: str,
) -> EntitySet:
    """
    Entry point for Stage 5. Tries the LLM first (generate_entities_with_llm),
    which can identify any entity type, not just pre-registered ones.
    Falls back to candidate_entities + fixed archetype dictionary if
    the LLM call fails or returns nothing usable.
    """
    start_time = time.perf_counter()
    logger_instance = Logger(trace_id=trace_id)
    logger_instance.log_event("entities.py", f"Starting entity generation | candidate_entities={raw_features.candidate_entities}")
    logger.info(
        "trace_id=%s | entities.py | stage=start | candidate_entities=%s",
        trace_id, raw_features.candidate_entities,
    )

    entities: List[Entity] = []

    fr_summaries = [{"fr_id": fr.fr_id, "description": fr.description} for fr in functional_set.requirements]
    llm_entities = generate_entities_with_llm(raw_features.normalized_text, fr_summaries, trace_id)

    if llm_entities is not None:
        logger_instance.log_event("entities.py", "Using LLM-generated entities (model path)")
        logger.info("trace_id=%s | entities.py | using LLM-generated entities (model path)", trace_id)
        name_to_index = {item["name"]: i for i, item in enumerate(llm_entities)}
        for index, item in enumerate(llm_entities, start=1):
            try:
                attributes = [
                    EntityAttribute(name=a["name"], type=AttributeType(a["type"]), required=a["required"])
                    for a in item["attributes"]
                ]
                relationships = [
                    EntityRelationship(
                        from_entity=item["name"],
                        to_entity=r["to_entity"],
                        relationship_type=RelationshipType(r["relationship_type"]),
                    )
                    for r in item["relationships"]
                    if r["to_entity"] in name_to_index
                ]
                source_fr_ids = [
                    fr.fr_id for fr in functional_set.requirements
                    if item["name"] in " ".join([fr.description.lower(), *fr.inputs, *fr.outputs]).lower()
                ]
                entity = Entity(
                    entity_id=_build_entity_id(index),
                    name=item["name"],
                    attributes=attributes,
                    relationships=relationships,
                    source_fr_ids=source_fr_ids,
                )
                entities.append(entity)
            except Exception as exc:  # noqa: BLE001
                logger_instance.log_event("entities.py", f"Failed to build entity from LLM item at index={index} | error={str(exc)}", level="CRITICAL")
                logger.critical(
                    "trace_id=%s | entities.py | failed to build entity from LLM item at index=%d | error=%s",
                    trace_id, index, str(exc), exc_info=True,
                )
                continue

    if not entities:
        logger_instance.log_event("entities.py", "LLM path unavailable/empty, falling back to archetype dictionary", level="WARNING")
        logger.warning(
            "trace_id=%s | entities.py | LLM path unavailable/empty, falling back to archetype dictionary",
            trace_id,
        )
        entities = _generate_via_rules(raw_features, functional_set, trace_id)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger_instance.log_event("entities.py", f"Stage complete | entity_count={len(entities)} duration_ms={elapsed_ms:.2f}")
    logger.info(
        "trace_id=%s | entities.py | stage=complete | entity_count=%d duration_ms=%.2f",
        trace_id, len(entities), elapsed_ms,
    )

    return EntitySet(trace_id=trace_id, entities=entities)