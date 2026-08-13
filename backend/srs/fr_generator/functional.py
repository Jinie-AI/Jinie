"""Stage 2: functional requirements, generated from the actual request."""
from __future__ import annotations

import logging
import re
import time
from typing import List

from common.schemas import FunctionalRequirement, FunctionalRequirementSet, Priority, RawRequirementFeatures
from logger import Logger
from .functional_model import generate_frs_with_llm

logger = logging.getLogger(__name__)
_VALID_PRIORITIES = {"critical", "high", "medium", "low"}


def _build_fr_id(index: int) -> str:
    return f"FR-{index:03d}"


def _fallback_requirements(features: RawRequirementFeatures) -> List[FunctionalRequirement]:
    """Offline fallback that restates the user's requested capabilities, not archetypes."""
    prompt = features.normalized_text.strip()
    clauses = [part.strip(" .") for part in re.split(r"[.;\n]+|\b(?:and then|then)\b", prompt, flags=re.I) if part.strip(" .")]
    clauses = clauses[:6] or ["Use the application as described in the request"]
    keywords = features.extracted_keywords or ["request"]
    requirements = []
    for index, clause in enumerate(clauses, 1):
        words = re.findall(r"[A-Za-z][A-Za-z0-9]*", clause.lower())
        inputs = [f"{word}_input" for word in words[:3] if word not in {"build", "create", "make", "want", "need", "users", "user"}] or ["request_input"]
        requirements.append(FunctionalRequirement(fr_id=_build_fr_id(index), description=f"The application shall support: {clause}.", actors=["User"], inputs=inputs[:3], outputs=["requested_result"], priority=Priority.HIGH if index == 1 else Priority.MEDIUM, source_keywords=[key for key in keywords if key in clause.lower()]))
    return requirements


def generate_functional_requirements(raw_features: RawRequirementFeatures, trace_id: str) -> FunctionalRequirementSet:
    start = time.perf_counter()
    audit = Logger(trace_id=trace_id)
    requirements: List[FunctionalRequirement] = []
    generated = generate_frs_with_llm(raw_features.normalized_text, raw_features.extracted_keywords, raw_features.intent_tags, trace_id)
    for index, item in enumerate(generated or [], 1):
        try:
            priority = item["priority"] if item["priority"] in _VALID_PRIORITIES else "medium"
            requirements.append(FunctionalRequirement(fr_id=_build_fr_id(index), description=item["description"], actors=item["actors"], inputs=item["inputs"], outputs=item["outputs"], priority=Priority(priority), source_keywords=[key for key in raw_features.extracted_keywords if key in item["description"].lower()]))
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("trace_id=%s | invalid LLM FR %d: %s", trace_id, index, exc)
    if not requirements:
        requirements = _fallback_requirements(raw_features)
        audit.log_event("functional.py", "LLM unavailable; used prompt-derived fallback", level="WARNING")
    audit.log_event("functional.py", f"Stage complete | fr_count={len(requirements)} duration_ms={(time.perf_counter()-start)*1000:.2f}")
    return FunctionalRequirementSet(trace_id=trace_id, requirements=requirements)
