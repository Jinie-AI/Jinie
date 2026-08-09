"""Stage 4: navigation topology derived from functional requirements."""
from __future__ import annotations

import re
import time
from typing import Dict, List

from common.schemas import FunctionalRequirement, FunctionalRequirementSet, NavigationEdge, ScreenType, Sitemap, SitemapNode
from logger import Logger
from .sitemap_model import generate_sitemap_with_llm


def _build_screen_id(index: int) -> str:
    return f"SCR-{index:03d}"


def _screen_type(fr: FunctionalRequirement) -> ScreenType:
    text = " ".join([fr.description, *fr.inputs, *fr.outputs]).lower()
    if any(term in text for term in ("sign in", "sign up", "login", "credential", "password", "authentication")):
        return ScreenType.AUTH
    if any(term in text for term in ("create", "edit", "update", "submit", "register", "book", "request")):
        return ScreenType.FORM
    if any(term in text for term in ("list", "search", "browse", "find", "history", "directory", "results")):
        return ScreenType.LIST
    if any(term in text for term in ("detail", "view ", "review")):
        return ScreenType.DETAIL
    if any(term in text for term in ("settings", "preference", "configuration")):
        return ScreenType.SETTINGS
    return ScreenType.GENERIC


def _screen_name(fr: FunctionalRequirement, index: int) -> str:
    ignored = {"the", "application", "shall", "support", "user", "users", "with", "from", "and", "for", "input", "result"}
    words = [word for word in re.findall(r"[A-Za-z][A-Za-z0-9]*", fr.description) if word.lower() not in ignored]
    stem = "".join(word.title() for word in words[:3]) or f"Workflow{index}"
    return f"{stem}Screen"


def _route(name: str) -> str:
    return "/" + re.sub(r"(?<!^)([A-Z])", r"-\1", name.removesuffix("Screen")).lower()


def _generate_via_rules(functional_set: FunctionalRequirementSet, trace_id: str) -> Sitemap:
    """One context-specific screen per requirement; no domain keyword table."""
    nodes: List[SitemapNode] = []
    used_names = set()
    for index, fr in enumerate(functional_set.requirements, 1):
        name = _screen_name(fr, index)
        if name in used_names:
            name = f"{name.removesuffix('Screen')}{index}Screen"
        used_names.add(name)
        nodes.append(SitemapNode(screen_id=_build_screen_id(index), screen_name=name, route=_route(name), screen_type=_screen_type(fr), linked_fr_ids=[fr.fr_id], is_entry_point=index == 1))
    edges = [NavigationEdge(from_screen_id=nodes[index - 1].screen_id, to_screen_id=nodes[index].screen_id, trigger="continue") for index in range(1, len(nodes))]
    return Sitemap(trace_id=trace_id, nodes=nodes, edges=edges)


def generate_sitemap(functional_set: FunctionalRequirementSet, trace_id: str) -> Sitemap:
    start = time.perf_counter()
    audit = Logger(trace_id=trace_id)
    summaries = [{"fr_id": fr.fr_id, "description": fr.description} for fr in functional_set.requirements]
    result = generate_sitemap_with_llm(summaries, trace_id)
    if result is None:
        audit.log_event("sitemap.py", "LLM unavailable; used FR-derived fallback", level="WARNING")
        return _generate_via_rules(functional_set, trace_id)
    names: Dict[str, str] = {}
    nodes: List[SitemapNode] = []
    for index, screen in enumerate(result["screens"], 1):
        screen_id = _build_screen_id(index)
        names[screen["screen_name"]] = screen_id
        nodes.append(SitemapNode(screen_id=screen_id, screen_name=screen["screen_name"], route=screen["route"], screen_type=ScreenType(screen["screen_type"]), linked_fr_ids=screen["linked_fr_ids"], is_entry_point=screen["is_entry_point"]))
    if nodes and not any(node.is_entry_point for node in nodes):
        nodes[0].is_entry_point = True
    edges = [NavigationEdge(from_screen_id=names[edge["from_screen"]], to_screen_id=names[edge["to_screen"]], trigger=edge["trigger"]) for edge in result["edges"] if edge["from_screen"] in names and edge["to_screen"] in names]
    audit.log_event("sitemap.py", f"Stage complete | screen_count={len(nodes)} duration_ms={(time.perf_counter()-start)*1000:.2f}")
    return Sitemap(trace_id=trace_id, nodes=nodes, edges=edges)
