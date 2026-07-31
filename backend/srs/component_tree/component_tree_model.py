"""
component_tree_model.py

Domain-specific LLM layer for Stage 6 (Component Tree). Given a
screen's name and type, asks the LLM to design a nested React Native
component layout directly, instead of picking from 8 fixed hardcoded
templates in component_tree.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List, Any, Dict

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()

_MAX_DEPTH = 6  # safety limit against pathologically deep/recursive LLM output


class ExtractedComponentNode(TypedDict):
    component_type: str
    props: Dict[str, Any]
    design_tokens: Dict[str, str]
    children: List["ExtractedComponentNode"]


_SYSTEM_PROMPT = """You are a React Native UI layout engine for a mobile \
app generation pipeline. Given a screen's name and category, design a \
nested component tree using standard React Native / Expo primitives \
(SafeAreaView, View, ScrollView, FlatList, Text, TextInput, Button, \
Image, TouchableOpacity, KeyboardAvoidingView, etc).

Respond with ONLY a single valid JSON object, no markdown fences, no \
preamble, no explanation, representing the ROOT node:

{
  "component_type": "e.g. SafeAreaView",
  "props": {"key": "value pairs of simple prop hints, e.g. style:'flex:1'"},
  "design_tokens": {"spacing": "sm|md|lg", "background": "surface.primary", \
"radius": "sm|md|lg"},
  "children": [ ...nested objects with the same shape... ]
}

Keep nesting to a reasonable depth (max 5 levels). Design a layout that \
actually fits the screen's purpose (e.g. an auth screen needs \
TextInput + Button, a feed needs FlatList, a dashboard needs chart-like \
elements)."""


def _build_user_prompt(screen_name: str, screen_type: str) -> str:
    return f"Screen name: {screen_name}\nScreen category: {screen_type}"


def _prune_depth(node: dict, depth: int = 0) -> dict:
    """Defensive guard: truncate children beyond _MAX_DEPTH to avoid runaway nesting."""
    if depth >= _MAX_DEPTH:
        node["children"] = []
        return node
    node["children"] = [_prune_depth(child, depth + 1) for child in node.get("children", [])]
    return node


def _sanitize_node(raw_node: Any) -> Optional[ExtractedComponentNode]:
    if not isinstance(raw_node, dict):
        return None
    try:
        children = []
        for child in raw_node.get("children", []):
            sanitized_child = _sanitize_node(child)
            if sanitized_child is not None:
                children.append(sanitized_child)

        node: ExtractedComponentNode = {
            "component_type": str(raw_node["component_type"]),
            "props": {str(k): v for k, v in raw_node.get("props", {}).items()} if isinstance(raw_node.get("props"), dict) else {},
            "design_tokens": {str(k): str(v) for k, v in raw_node.get("design_tokens", {}).items()} if isinstance(raw_node.get("design_tokens"), dict) else {},
            "children": children,
        }
        return node
    except (KeyError, TypeError):
        return None


def generate_component_tree_with_llm(
    screen_name: str, screen_type: str, trace_id: str
) -> Optional[ExtractedComponentNode]:
    """
    Calls the LLM to design a nested component tree for one screen.
    Returns None (never raises) on any failure — caller falls back to
    the fixed template builder in component_tree.py.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(screen_name, screen_type)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.4, max_tokens=1000)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | component_tree_model.py | LLM call failed for screen=%s, caller should fall back | error=%s",
            trace_id, screen_name, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning(
            "trace_id=%s | component_tree_model.py | LLM response was not valid JSON for screen=%s | error=%s",
            trace_id, screen_name, str(exc),
        )
        return None

    root = _sanitize_node(parsed)
    if root is None:
        logger.warning(
            "trace_id=%s | component_tree_model.py | LLM response had wrong shape for screen=%s",
            trace_id, screen_name,
        )
        return None

    root = _prune_depth(root)
    logger.info(
        "trace_id=%s | component_tree_model.py | LLM generated component tree for screen=%s",
        trace_id, screen_name,
    )
    return root