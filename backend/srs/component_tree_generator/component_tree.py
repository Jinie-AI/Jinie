"""Build screen-specific component trees for the SRS pipeline.

The model receives the user's requirement and the screen's linked functional
requirements.  If it is unavailable, the fallback still derives a useful,
domain-neutral layout from that same context; it never selects a product,
social, music, or analytics template.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Dict, List, Optional

from common.schemas import ComponentNode, ComponentTree, ComponentTreeSet, FunctionalRequirementSet, Sitemap
from logger import Logger
from .component_tree_model import generate_component_tree_with_llm

logger = logging.getLogger(__name__)

_DEFAULT_DESIGN_TOKENS = {"spacing": "md", "background": "surface.primary", "radius": "md"}
_GENERIC_TERMS = {"the", "and", "for", "with", "from", "that", "this", "user", "users", "system", "application", "app", "shall", "support", "manage", "view", "create", "update", "delete", "allow"}


def _new_component_id(screen_id: str, counter: int) -> str:
    return f"{screen_id}-CMP-{counter:03d}"


def _words(value: str) -> List[str]:
    return [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z0-9]*", value) if word.lower() not in _GENERIC_TERMS]


def _title(screen_name: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r" \1", screen_name).removesuffix(" Screen").strip() or "Workspace"


def _fallback_tree(screen_id: str, screen_name: str, requirement_text: str) -> ComponentNode:
    """Create a small, meaningful layout using only the current screen context."""
    counter = [0]

    def node(component_type: str, props: Optional[dict] = None, children: Optional[List[ComponentNode]] = None) -> ComponentNode:
        counter[0] += 1
        return ComponentNode(component_id=_new_component_id(screen_id, counter[0]), component_type=component_type,
                             props=props or {}, design_tokens=_DEFAULT_DESIGN_TOKENS, children=children or [])

    title = _title(screen_name)
    context = f"{screen_name} {requirement_text}".lower()
    terms = _words(requirement_text) or _words(screen_name) or ["information"]
    subject = " ".join(terms[:3]).title()
    children: List[ComponentNode] = [node("Header", {"title": title})]

    # These are interaction concepts, not application-domain templates.
    if any(token in context for token in ("auth", "login", "sign in", "password", "authentication")):
        children.append(node("Form", {"accessibilityLabel": f"{title} sign-in form"}, [
            node("TextInput", {"placeholder": "Email address"}),
            node("TextInput", {"placeholder": "Password", "secureTextEntry": True}),
            node("Button", {"label": "Sign in"}),
        ]))
    elif any(token in context for token in ("search", "find", "filter", "lookup")):
        children.append(node("TextInput", {"placeholder": f"Search {subject.lower()}"}))
    if any(token in context for token in ("create", "add", "submit", "register", "edit", "update", "request", "book")):
        fields = [node("TextInput", {"placeholder": f"Enter {term.replace('_', ' ')}"}) for term in terms[:3]]
        fields.append(node("Button", {"label": f"Save {subject}"}))
        children.append(node("Form", {"accessibilityLabel": f"{title} form"}, fields))
    elif any(token in context for token in ("list", "browse", "search", "history", "records", "catalog", "directory", "results")):
        card = node("Card", {"title": subject, "onPress": f"open{''.join(word.title() for word in terms[:2])}"}, [node("Text", {"content": f"{subject} summary"})])
        children.append(node("FlatList", {"data": f"{''.join(terms[:2]) or 'items'}Items", "keyExtractor": "id"}, [card]))
    elif any(token in context for token in ("report", "metric", "analytics", "summary", "overview", "status")):
        children.append(node("Section", {"title": f"{subject} summary"}, [node("Text", {"content": f"Current {subject.lower()}"})]))
    else:
        children.append(node("ScrollView", {}, [node("Text", {"content": requirement_text or f"Manage {subject}"}), node("Button", {"label": f"Continue with {subject}"})]))
    return node("SafeAreaView", {"style": "flex:1"}, children)


def _convert_llm_node_to_component_node(raw_node: dict, screen_id: str, counter: list) -> ComponentNode:
    counter[0] += 1
    return ComponentNode(
        component_id=_new_component_id(screen_id, counter[0]), component_type=raw_node["component_type"],
        props=raw_node.get("props", {}), design_tokens=raw_node.get("design_tokens", {}) or _DEFAULT_DESIGN_TOKENS,
        children=[_convert_llm_node_to_component_node(child, screen_id, counter) for child in raw_node.get("children", [])],
    )


def generate_component_trees(sitemap: Sitemap, trace_id: str, functional_set: Optional[FunctionalRequirementSet] = None,
                             app_description: str = "") -> ComponentTreeSet:
    """Generate a tailored tree per sitemap node while preserving the public output schema."""
    start_time = time.perf_counter()
    audit = Logger(trace_id=trace_id)
    descriptions: Dict[str, str] = {}
    if functional_set:
        descriptions = {fr.fr_id: fr.description for fr in functional_set.requirements}
    trees: List[ComponentTree] = []

    for screen in sitemap.nodes:
        linked = [descriptions[fr_id] for fr_id in screen.linked_fr_ids if fr_id in descriptions]
        requirement_text = " ".join(linked) or app_description or screen.screen_name
        llm_root = generate_component_tree_with_llm(
            screen_name=screen.screen_name, screen_type=screen.screen_type.value, trace_id=trace_id,
            app_description=app_description, requirement_text=requirement_text,
        )
        try:
            root = _convert_llm_node_to_component_node(llm_root, screen.screen_id, [0]) if llm_root else _fallback_tree(screen.screen_id, screen.screen_name, requirement_text)
            trees.append(ComponentTree(screen_id=screen.screen_id, screen_name=screen.screen_name, root=root))
        except Exception as exc:  # noqa: BLE001
            logger.exception("trace_id=%s | component tree failed for screen=%s", trace_id, screen.screen_name)
            audit.log_event("component_tree.py", f"Screen tree failed for {screen.screen_name}: {exc}", level="CRITICAL")

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    audit.log_event("component_tree.py", f"Stage complete | tree_count={len(trees)} duration_ms={elapsed_ms:.2f}")
    return ComponentTreeSet(trace_id=trace_id, trees=trees)
