"""LLM adapter for domain-independent, screen-specific component trees."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

from shared.json_utils import strip_markdown_fences
from shared.llm_client import LLMAPIError, LLMClient

logger = logging.getLogger(__name__)
_client = LLMClient()
_MAX_DEPTH = 6


class ExtractedComponentNode(TypedDict):
    component_type: str
    props: Dict[str, Any]
    design_tokens: Dict[str, str]
    children: List["ExtractedComponentNode"]


_SYSTEM_PROMPT = """You design React Native mobile layouts from product requirements. Return ONLY one valid JSON root node with component_type, props, design_tokens, and children. Use standard React Native primitives or neutral semantic components such as Header, Card, Form, Table, Section, and EmptyState. Design the exact screen described by the supplied application and functional requirement: include a meaningful header title, button labels, and input placeholders. Choose lists, cards, forms, tables, details, or summaries only when supported by that requirement. Never invent a domain, and never reuse music, social, commerce, or dashboard examples unless they are explicitly in the requirement. Keep nesting to five levels."""


def _build_user_prompt(screen_name: str, screen_type: str, app_description: str, requirement_text: str) -> str:
    return f"Application request:\n{app_description or 'Not separately provided'}\n\nScreen: {screen_name}\nScreen category hint: {screen_type}\n\nFunctional requirements served by this screen:\n{requirement_text}"


def _prune_depth(node: dict, depth: int = 0) -> dict:
    if depth >= _MAX_DEPTH:
        node["children"] = []
    else:
        node["children"] = [_prune_depth(child, depth + 1) for child in node.get("children", [])]
    return node


def _sanitize_node(raw_node: Any) -> Optional[ExtractedComponentNode]:
    if not isinstance(raw_node, dict) or not raw_node.get("component_type"):
        return None
    children = [child for item in raw_node.get("children", []) if (child := _sanitize_node(item)) is not None]
    return {"component_type": str(raw_node["component_type"]), "props": {str(k): v for k, v in raw_node.get("props", {}).items()} if isinstance(raw_node.get("props"), dict) else {}, "design_tokens": {str(k): str(v) for k, v in raw_node.get("design_tokens", {}).items()} if isinstance(raw_node.get("design_tokens"), dict) else {}, "children": children}


def generate_component_tree_with_llm(screen_name: str, screen_type: str, trace_id: str, app_description: str = "", requirement_text: str = "") -> Optional[ExtractedComponentNode]:
    try:
        response = _client.chat_completion(messages=[{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": _build_user_prompt(screen_name, screen_type, app_description, requirement_text)}], trace_id=trace_id, temperature=0.25, max_tokens=1300)
        root = _sanitize_node(json.loads(strip_markdown_fences(response)))
        return _prune_depth(root) if root else None
    except (LLMAPIError, json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning("trace_id=%s | component tree LLM unavailable for %s: %s", trace_id, screen_name, exc)
        return None
