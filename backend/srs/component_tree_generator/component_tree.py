"""
component_tree.py

Stage 6 of the SRS pipeline. Breaks down each screen from the Sitemap
into a nested, component-oriented layout tree using React Native
primitives and design tokens (e.g. SafeAreaView -> View -> FlatList).
This is the structural scaffold Module 05 (Component Generator) will
later fill in with actual generated TSX code.

Primary path: calls the LLM (via component_tree_model.py) per screen
to design a layout tailored to that screen's purpose, instead of
picking from 8 fixed hardcoded templates.

Fallback path: if the LLM call fails for a screen, uses the fixed
template builder functions below (deterministic, offline).
"""

from __future__ import annotations

import logging
import time
from typing import List, Dict

from common.schemas import (
    Sitemap,
    SitemapNode,
    ScreenType,
    ComponentNode,
    ComponentTree,
    ComponentTreeSet,
)
from component_tree_generator.component_tree_model import generate_component_tree_with_llm
from logger import Logger

logger = logging.getLogger(__name__)


_DEFAULT_DESIGN_TOKENS = {
    "spacing": "md",
    "background": "surface.primary",
    "radius": "md",
}


def _new_component_id(screen_id: str, counter: int) -> str:
    return f"{screen_id}-CMP-{counter:03d}"


def _build_auth_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(
                component_id=cid(),
                component_type="KeyboardAvoidingView",
                props={"behavior": "padding"},
                children=[
                    ComponentNode(component_id=cid(), component_type="TextInput", props={"placeholder": "Email"}),
                    ComponentNode(component_id=cid(), component_type="TextInput", props={"placeholder": "Password", "secureTextEntry": True}),
                    ComponentNode(component_id=cid(), component_type="Button", props={"label": "Continue"}),
                ],
            )
        ],
    )


def _build_feed_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(component_id=cid(), component_type="Header", props={"title": "Feed"}),
            ComponentNode(
                component_id=cid(),
                component_type="FlatList",
                props={"data": "feedItems", "keyExtractor": "id"},
                children=[
                    ComponentNode(component_id=cid(), component_type="PostCard", props={"onPress": "openPost"}),
                ],
            ),
        ],
    )


def _build_list_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(component_id=cid(), component_type="SearchBar", props={"placeholder": "Search"}),
            ComponentNode(
                component_id=cid(),
                component_type="FlatList",
                props={"data": "items", "numColumns": 2},
                children=[
                    ComponentNode(component_id=cid(), component_type="ItemCard", props={"onPress": "openItem"}),
                ],
            ),
        ],
    )


def _build_form_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(component_id=cid(), component_type="ScrollView", props={}, children=[
                ComponentNode(component_id=cid(), component_type="FormField", props={"label": "Field"}),
                ComponentNode(component_id=cid(), component_type="Button", props={"label": "Submit"}),
            ]),
        ],
    )


def _build_profile_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(component_id=cid(), component_type="Avatar", props={"source": "avatarUrl"}),
            ComponentNode(component_id=cid(), component_type="Text", props={"content": "displayName"}),
            ComponentNode(component_id=cid(), component_type="Button", props={"label": "Edit Profile"}),
        ],
    )


def _build_dashboard_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(component_id=cid(), component_type="ScrollView", props={}, children=[
                ComponentNode(component_id=cid(), component_type="MetricCard", props={"metric": "value"}),
                ComponentNode(component_id=cid(), component_type="ChartView", props={"type": "line"}),
            ]),
        ],
    )


def _build_generic_tree(screen_id: str) -> ComponentNode:
    counter = [0]

    def cid() -> str:
        counter[0] += 1
        return _new_component_id(screen_id, counter[0])

    return ComponentNode(
        component_id=cid(),
        component_type="SafeAreaView",
        props={"style": "flex:1"},
        design_tokens=_DEFAULT_DESIGN_TOKENS,
        children=[
            ComponentNode(component_id=cid(), component_type="View", props={}, children=[
                ComponentNode(component_id=cid(), component_type="Text", props={"content": "Placeholder content"}),
            ]),
        ],
    )


_SCREEN_TYPE_BUILDERS = {
    ScreenType.AUTH: _build_auth_tree,
    ScreenType.FEED: _build_feed_tree,
    ScreenType.LIST: _build_list_tree,
    ScreenType.FORM: _build_form_tree,
    ScreenType.PROFILE: _build_profile_tree,
    ScreenType.DASHBOARD: _build_dashboard_tree,
    ScreenType.DETAIL: _build_generic_tree,
    ScreenType.SETTINGS: _build_form_tree,
    ScreenType.GENERIC: _build_generic_tree,
}


def _convert_llm_node_to_component_node(raw_node: dict, screen_id: str, counter: list) -> ComponentNode:
    """Recursively converts the LLM's plain-dict tree into real ComponentNode objects with scoped IDs."""
    counter[0] += 1
    component_id = _new_component_id(screen_id, counter[0])
    children = [
        _convert_llm_node_to_component_node(child, screen_id, counter)
        for child in raw_node.get("children", [])
    ]
    return ComponentNode(
        component_id=component_id,
        component_type=raw_node["component_type"],
        props=raw_node.get("props", {}),
        design_tokens=raw_node.get("design_tokens", {}) or _DEFAULT_DESIGN_TOKENS,
        children=children,
    )


def generate_component_trees(sitemap: Sitemap, trace_id: str) -> ComponentTreeSet:
    """
    Entry point for Stage 6. Tries the LLM first (generate_component_tree_with_llm)
    for each screen individually, so layouts are tailored per screen
    rather than picked from 8 fixed templates. Falls back to the fixed
    template builder for any screen where the LLM call fails.
    """
    start_time = time.perf_counter()
    logger_instance = Logger(trace_id=trace_id)
    logger_instance.log_event("component_tree.py", f"Starting component tree generation | screen_count={len(sitemap.nodes)}")
    logger.info(
        "trace_id=%s | component_tree.py | stage=start | screen_count=%d",
        trace_id, len(sitemap.nodes),
    )

    trees: List[ComponentTree] = []

    for node in sitemap.nodes:
        llm_root = generate_component_tree_with_llm(node.screen_name, node.screen_type.value, trace_id)

        if llm_root is not None:
            try:
                counter = [0]
                root = _convert_llm_node_to_component_node(llm_root, node.screen_id, counter)
                trees.append(ComponentTree(screen_id=node.screen_id, screen_name=node.screen_name, root=root))
                logger_instance.log_event("component_tree.py", f"Using LLM-generated tree for screen={node.screen_name} (model path)")
                logger.info(
                    "trace_id=%s | component_tree.py | using LLM-generated tree for screen=%s (model path)",
                    trace_id, node.screen_name,
                )
                continue
            except Exception as exc:  # noqa: BLE001
                logger_instance.log_event("component_tree.py", f"Failed to convert LLM tree for screen={node.screen_name} | error={str(exc)}", level="CRITICAL")
                logger.critical(
                    "trace_id=%s | component_tree.py | failed to convert LLM tree for screen=%s | error=%s",
                    trace_id, node.screen_name, str(exc), exc_info=True,
                )
                # fall through to template path below

        logger_instance.log_event("component_tree.py", f"LLM path unavailable/failed for screen={node.screen_name}, falling back to template", level="WARNING")
        logger.warning(
            "trace_id=%s | component_tree.py | LLM path unavailable/failed for screen=%s, falling back to template",
            trace_id, node.screen_name,
        )
        try:
            builder = _SCREEN_TYPE_BUILDERS.get(node.screen_type, _build_generic_tree)
            root = builder(node.screen_id)
            trees.append(ComponentTree(screen_id=node.screen_id, screen_name=node.screen_name, root=root))
            logger.debug(
                "trace_id=%s | component_tree.py | built template tree for screen=%s using builder=%s",
                trace_id, node.screen_name, builder.__name__,
            )
        except Exception as exc:  # noqa: BLE001
            logger_instance.log_event("component_tree.py", f"Failed to build template tree for screen={node.screen_name} | error={str(exc)}", level="CRITICAL")
            logger.critical(
                "trace_id=%s | component_tree.py | failed to build template tree for screen=%s | error=%s",
                trace_id, node.screen_name, str(exc), exc_info=True,
            )
            try:
                fallback_root = _build_generic_tree(node.screen_id)
                trees.append(ComponentTree(screen_id=node.screen_id, screen_name=node.screen_name, root=fallback_root))
                logger.warning(
                    "trace_id=%s | component_tree.py | fell back to generic tree for screen=%s",
                    trace_id, node.screen_name,
                )
            except Exception as fallback_exc:  # noqa: BLE001
                logger_instance.log_event("component_tree.py", f"Fallback tree construction also failed for screen={node.screen_name} | error={str(fallback_exc)}", level="CRITICAL")
                logger.critical(
                    "trace_id=%s | component_tree.py | fallback tree construction also failed for screen=%s | error=%s",
                    trace_id, node.screen_name, str(fallback_exc), exc_info=True,
                )
                continue

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger_instance.log_event("component_tree.py", f"Stage complete | tree_count={len(trees)} duration_ms={elapsed_ms:.2f}")
    logger.info(
        "trace_id=%s | component_tree.py | stage=complete | tree_count=%d duration_ms=%.2f",
        trace_id, len(trees), elapsed_ms,
    )

    return ComponentTreeSet(trace_id=trace_id, trees=trees)