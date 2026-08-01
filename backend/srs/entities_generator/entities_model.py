"""
entities_model.py

Domain-specific LLM layer for Stage 5 (Entities). Given the app
description and FR list, asks the LLM to identify persistable data
objects, their attributes, and relationships directly, instead of
relying only on the fixed entity dictionary in entities.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()

_VALID_ATTRIBUTE_TYPES = {
    "string", "number", "boolean", "date", "timestamp", "array", "object", "reference",
}
_VALID_RELATIONSHIP_TYPES = {"one_to_one", "one_to_many", "many_to_many"}


class ExtractedAttribute(TypedDict):
    name: str
    type: str
    required: bool


class ExtractedRelationship(TypedDict):
    to_entity: str
    relationship_type: str


class ExtractedEntity(TypedDict):
    name: str
    attributes: List[ExtractedAttribute]
    relationships: List[ExtractedRelationship]


_SYSTEM_PROMPT = """You are a data modeling engine for a mobile app \
generation pipeline. Given an app description and its Functional \
Requirements, identify the persistable data entities (database objects) \
the app needs to store, along with their attributes and relationships \
to other entities.

Respond with ONLY a single valid JSON array, no markdown fences, no \
preamble, no explanation. Each array item must have exactly these keys:

{
  "name": "lowercase singular noun, e.g. 'user', 'post', 'order'",
  "attributes": [
    {"name": "snake_case_field_name", "type": "string" | "number" | \
"boolean" | "date" | "timestamp" | "array" | "object" | "reference", \
"required": true | false}
  ],
  "relationships": [
    {"to_entity": "name of another entity in this same array", \
"relationship_type": "one_to_one" | "one_to_many" | "many_to_many"}
  ]
}

Only include relationships where "to_entity" is also one of the \
entities you returned. Every entity should have an id field and \
reasonable core fields (e.g. a user entity needs at least an id and \
identifying field). Do not invent entities unrelated to the description."""


def _build_user_prompt(normalized_text: str, fr_summaries: List[dict]) -> str:
    fr_lines = "\n".join(f"- {fr['fr_id']}: {fr['description']}" for fr in fr_summaries)
    return f"App description:\n\"\"\"\n{normalized_text}\n\"\"\"\n\nFunctional Requirements:\n{fr_lines}"


def generate_entities_with_llm(
    normalized_text: str, fr_summaries: List[dict], trace_id: str
) -> Optional[List[ExtractedEntity]]:
    """
    Calls the LLM to identify entities, attributes, and relationships.
    Returns None (never raises) on any failure — caller falls back to
    the fixed entity dictionary in entities.py.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(normalized_text, fr_summaries)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.3, max_tokens=1500)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | entities_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON array of entity objects")
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "trace_id=%s | entities_model.py | LLM response was not a valid JSON array | error=%s | raw=%s",
            trace_id, str(exc), cleaned[:300],
        )
        return None

    entities: List[ExtractedEntity] = []
    entity_names_seen = set()

    for index, item in enumerate(parsed):
        try:
            attributes: List[ExtractedAttribute] = []
            for attr in item.get("attributes", []):
                attr_type = str(attr.get("type", "string")).lower()
                if attr_type not in _VALID_ATTRIBUTE_TYPES:
                    attr_type = "string"
                attributes.append({
                    "name": str(attr["name"]),
                    "type": attr_type,
                    "required": bool(attr.get("required", True)),
                })

            entity: ExtractedEntity = {
                "name": str(item["name"]).lower(),
                "attributes": attributes,
                "relationships": [],  # filled in second pass below once all names are known
            }
            entities.append(entity)
            entity_names_seen.add(entity["name"])
        except (KeyError, TypeError) as exc:
            logger.warning(
                "trace_id=%s | entities_model.py | skipping malformed entity item at index=%d | error=%s",
                trace_id, index, str(exc),
            )
            continue

    # second pass: attach relationships now that we know all valid entity names
    for index, item in enumerate(parsed):
        if index >= len(entities):
            continue
        for rel in item.get("relationships", []):
            try:
                to_entity = str(rel["to_entity"]).lower()
                rel_type = str(rel.get("relationship_type", "one_to_many")).lower()
                if to_entity not in entity_names_seen or rel_type not in _VALID_RELATIONSHIP_TYPES:
                    continue
                entities[index]["relationships"].append({"to_entity": to_entity, "relationship_type": rel_type})
            except (KeyError, TypeError):
                continue

    if not entities:
        logger.warning("trace_id=%s | entities_model.py | LLM returned zero usable entities", trace_id)
        return None

    logger.info(
        "trace_id=%s | entities_model.py | LLM generated %d entities successfully",
        trace_id, len(entities),
    )
    return entities