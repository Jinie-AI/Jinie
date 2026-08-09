"""
sitemap.py

Stage 4 of the SRS pipeline. Compiles the layout navigation topology:
maps Functional Requirements to individual application screens/routes
(e.g. AuthScreen, MainFeed) and derives the navigation edges between
them (which screen leads to which, and on what trigger).

Primary path: calls the LLM (via sitemap_model.py) to design screens
and navigation edges directly from the FR list, so it isn't limited to
pre-anticipated screen categories.

Fallback path: if the LLM call fails, uses the fixed keyword-lookup
table below (deterministic, offline).
"""

from __future__ import annotations

import logging
import time
from typing import List, Dict

from common.schemas import (
    FunctionalRequirementSet,
    FunctionalRequirement,
    Sitemap,
    SitemapNode,
    NavigationEdge,
    ScreenType,
)
from .sitemap_model import generate_sitemap_with_llm
from logger import Logger

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Keyword -> screen archetype mapping
# ---------------------------------------------------------------------

_SCREEN_KEYWORD_MAP = [
    (["register", "login", "password", "auth_token"], "AuthScreen", "/auth", ScreenType.AUTH, True),
    (["feed_items_list", "post", "created_post_object"], "MainFeed", "/feed", ScreenType.FEED, False),
    (["product_list", "category_filter", "search_query"], "ProductCatalog", "/catalog", ScreenType.LIST, False),
    (["order_confirmation", "payment_method"], "CheckoutScreen", "/checkout", ScreenType.FORM, False),
    (["message_text", "recipient_id"], "ChatScreen", "/chat", ScreenType.GENERIC, False),
    (["updated_profile_object", "display_name", "avatar_image"], "ProfileScreen", "/profile", ScreenType.PROFILE, False),
    (["aggregated_metrics", "date_range_filter"], "DashboardScreen", "/dashboard", ScreenType.DASHBOARD, False),
]

_DEFAULT_SCREEN = ("HomeScreen", "/home", ScreenType.GENERIC, True)


def _matches_any(fr: FunctionalRequirement, keywords: List[str]) -> bool:
    haystack = " ".join([fr.description.lower(), *[i.lower() for i in fr.inputs], *[o.lower() for o in fr.outputs]])
    return any(kw.lower() in haystack for kw in keywords)


def _build_screen_id(index: int) -> str:
    return f"SCR-{index:03d}"


def _generate_via_rules(functional_set: FunctionalRequirementSet, trace_id: str) -> Sitemap:
    """Fallback path: fixed keyword-lookup table (deterministic, offline)."""
    screen_registry: Dict[str, SitemapNode] = {}
    screen_counter = 1
    fr_to_screen_name: Dict[str, str] = {}

    for fr in functional_set.requirements:
        try:
            matched = False
            for keywords, screen_name, route, screen_type, is_entry in _SCREEN_KEYWORD_MAP:
                if _matches_any(fr, keywords):
                    if screen_name not in screen_registry:
                        node = SitemapNode(
                            screen_id=_build_screen_id(screen_counter),
                            screen_name=screen_name,
                            route=route,
                            screen_type=screen_type,
                            linked_fr_ids=[fr.fr_id],
                            is_entry_point=is_entry,
                        )
                        screen_registry[screen_name] = node
                        screen_counter += 1
                        logger.debug("trace_id=%s | sitemap.py | created screen=%s for fr_id=%s", trace_id, screen_name, fr.fr_id)
                    else:
                        screen_registry[screen_name].linked_fr_ids.append(fr.fr_id)
                    fr_to_screen_name[fr.fr_id] = screen_name
                    matched = True
                    break

            if not matched:
                screen_name, route, screen_type, is_entry = _DEFAULT_SCREEN
                if screen_name not in screen_registry:
                    node = SitemapNode(
                        screen_id=_build_screen_id(screen_counter),
                        screen_name=screen_name,
                        route=route,
                        screen_type=screen_type,
                        linked_fr_ids=[fr.fr_id],
                        is_entry_point=is_entry,
                    )
                    screen_registry[screen_name] = node
                    screen_counter += 1
                else:
                    screen_registry[screen_name].linked_fr_ids.append(fr.fr_id)
                fr_to_screen_name[fr.fr_id] = screen_name
                logger.debug(
                    "trace_id=%s | sitemap.py | fr_id=%s did not match any archetype, routed to default HomeScreen",
                    trace_id, fr.fr_id,
                )

        except Exception as exc:  # noqa: BLE001
            logger.critical(
                "trace_id=%s | sitemap.py | failed to route fr_id=%s to a screen | error=%s",
                trace_id, fr.fr_id, str(exc), exc_info=True,
            )
            continue

    nodes = list(screen_registry.values())
    if not any(n.is_entry_point for n in nodes) and nodes:
        nodes[0].is_entry_point = True
        logger.debug("trace_id=%s | sitemap.py | no entry point detected, defaulting to first screen=%s", trace_id, nodes[0].screen_name)

    edges: List[NavigationEdge] = []
    entry_nodes = [n for n in nodes if n.is_entry_point]
    non_entry_nodes = [n for n in nodes if not n.is_entry_point]
    try:
        for entry in entry_nodes:
            for target in non_entry_nodes:
                edges.append(
                    NavigationEdge(
                        from_screen_id=entry.screen_id,
                        to_screen_id=target.screen_id,
                        trigger="on_auth_success" if entry.screen_type == ScreenType.AUTH else "navigate",
                    )
                )
    except Exception as exc:  # noqa: BLE001
        logger.critical("trace_id=%s | sitemap.py | edge construction failed | error=%s", trace_id, str(exc), exc_info=True)

    return Sitemap(trace_id=trace_id, nodes=nodes, edges=edges)


def generate_sitemap(functional_set: FunctionalRequirementSet, trace_id: str) -> Sitemap:
    """
    Entry point for Stage 4. Tries the LLM first (generate_sitemap_with_llm),
    which can design screens/edges for any app description. Falls back
    to the fixed keyword-lookup table if the LLM call fails or returns
    nothing usable.
    """
    start_time = time.perf_counter()
    logger_instance = Logger(trace_id=trace_id)
    logger_instance.log_event("sitemap.py", f"Starting sitemap generation | fr_count={len(functional_set.requirements)}")
    logger.info(
        "trace_id=%s | sitemap.py | stage=start | fr_count=%d",
        trace_id, len(functional_set.requirements),
    )

    fr_summaries = [{"fr_id": fr.fr_id, "description": fr.description} for fr in functional_set.requirements]
    llm_result = generate_sitemap_with_llm(fr_summaries, trace_id)

    nodes: List[SitemapNode] = []
    edges: List[NavigationEdge] = []

    if llm_result is not None:
        logger_instance.log_event("sitemap.py", "Using LLM-generated sitemap (model path)")
        logger.info("trace_id=%s | sitemap.py | using LLM-generated sitemap (model path)", trace_id)
        screen_name_to_id: Dict[str, str] = {}
        for index, screen in enumerate(llm_result["screens"], start=1):
            try:
                screen_id = _build_screen_id(index)
                node = SitemapNode(
                    screen_id=screen_id,
                    screen_name=screen["screen_name"],
                    route=screen["route"],
                    screen_type=ScreenType(screen["screen_type"]),
                    linked_fr_ids=screen["linked_fr_ids"],
                    is_entry_point=screen["is_entry_point"],
                )
                nodes.append(node)
                screen_name_to_id[screen["screen_name"]] = screen_id
            except Exception as exc:  # noqa: BLE001
                logger_instance.log_event("sitemap.py", f"Failed to build screen node from LLM item at index={index} | error={str(exc)}", level="CRITICAL")
                logger.critical(
                    "trace_id=%s | sitemap.py | failed to build screen node from LLM item at index=%d | error=%s",
                    trace_id, index, str(exc), exc_info=True,
                )
                continue

        if nodes and not any(n.is_entry_point for n in nodes):
            nodes[0].is_entry_point = True

        for edge_item in llm_result["edges"]:
            try:
                edges.append(
                    NavigationEdge(
                        from_screen_id=screen_name_to_id[edge_item["from_screen"]],
                        to_screen_id=screen_name_to_id[edge_item["to_screen"]],
                        trigger=edge_item["trigger"],
                    )
                )
            except Exception as exc:  # noqa: BLE001
                logger_instance.log_event("sitemap.py", f"Failed to build edge from LLM item | error={str(exc)}", level="CRITICAL")
                logger.critical(
                    "trace_id=%s | sitemap.py | failed to build edge from LLM item | error=%s",
                    trace_id, str(exc), exc_info=True,
                )
                continue

    if not nodes:
        logger_instance.log_event("sitemap.py", "LLM path unavailable/empty, falling back to keyword-lookup rules", level="WARNING")
        logger.warning(
            "trace_id=%s | sitemap.py | LLM path unavailable/empty, falling back to keyword-lookup rules",
            trace_id,
        )
        return _generate_via_rules(functional_set, trace_id)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger_instance.log_event("sitemap.py", f"Stage complete | screen_count={len(nodes)} edge_count={len(edges)} duration_ms={elapsed_ms:.2f}")
    logger.info(
        "trace_id=%s | sitemap.py | stage=complete | screen_count=%d edge_count=%d duration_ms=%.2f",
        trace_id, len(nodes), len(edges), elapsed_ms,
    )

    return Sitemap(trace_id=trace_id, nodes=nodes, edges=edges)