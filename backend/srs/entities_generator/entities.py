"""Stage 5: infer data entities without a fixed domain catalog."""
from __future__ import annotations

import logging
import re
import time
from typing import List

from common.schemas import AttributeType, Entity, EntityAttribute, EntitySet, FunctionalRequirementSet, RawRequirementFeatures
from logger import Logger
from .entities_model import generate_entities_with_llm

logger = logging.getLogger(__name__)
_IGNORE = {"app", "application", "user", "users", "build", "create", "make", "want", "need", "with", "from", "that", "this", "result", "input", "requested"}


def _build_entity_id(index: int) -> str:
    return f"ENT-{index:03d}"


def _fallback_names(features: RawRequirementFeatures, functional_set: FunctionalRequirementSet) -> List[str]:
    names = list(features.candidate_entities)
    for fr in functional_set.requirements:
        names.extend(fr.inputs)
        names.extend(fr.outputs)
    normalized = []
    for name in names:
        name = re.sub(r"_(input|result|response|list)$", "", name.lower()).strip("_")
        if len(name) > 2 and name not in _IGNORE and name not in normalized:
            normalized.append(name)
    return normalized[:8]


def _generate_via_rules(features: RawRequirementFeatures, functional_set: FunctionalRequirementSet) -> List[Entity]:
    entities = []
    for index, name in enumerate(_fallback_names(features, functional_set), 1):
        source_ids = [fr.fr_id for fr in functional_set.requirements if name in " ".join([fr.description.lower(), *fr.inputs, *fr.outputs]).lower()]
        entities.append(Entity(entity_id=_build_entity_id(index), name=name, attributes=[EntityAttribute(name=f"{name}_id", type=AttributeType.STRING), EntityAttribute(name="name", type=AttributeType.STRING, required=False), EntityAttribute(name="created_at", type=AttributeType.TIMESTAMP, required=False)], relationships=[], source_fr_ids=source_ids))
    return entities


def generate_entities(raw_features: RawRequirementFeatures, functional_set: FunctionalRequirementSet, trace_id: str) -> EntitySet:
    start = time.perf_counter()
    audit = Logger(trace_id=trace_id)
    summaries = [{"fr_id": fr.fr_id, "description": fr.description} for fr in functional_set.requirements]
    generated = generate_entities_with_llm(raw_features.normalized_text, summaries, trace_id)
    entities: List[Entity] = []
    for index, item in enumerate(generated or [], 1):
        try:
            entities.append(Entity(entity_id=_build_entity_id(index), name=item["name"], attributes=[EntityAttribute(name=attribute["name"], type=AttributeType(attribute["type"]), required=attribute["required"]) for attribute in item["attributes"]], relationships=[], source_fr_ids=[fr.fr_id for fr in functional_set.requirements if item["name"].lower() in fr.description.lower()]))
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("trace_id=%s | invalid LLM entity %d: %s", trace_id, index, exc)
    if not entities:
        entities = _generate_via_rules(raw_features, functional_set)
        audit.log_event("entities.py", "LLM unavailable; used prompt-derived entity fallback", level="WARNING")
    audit.log_event("entities.py", f"Stage complete | entity_count={len(entities)} duration_ms={(time.perf_counter()-start)*1000:.2f}")
    return EntitySet(trace_id=trace_id, entities=entities)
