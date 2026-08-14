"""
generator.py

Stage 5 entry point. Tries the LLM first (generator_model.py) to
render an already-built Component Tree into real React Native code,
so components are tailored per-tree rather than assembled from fixed
Python rendering rules. Falls back to the deterministic rule-based
renderer below if the LLM call fails or its output doesn't pass
validation (generator_validator.py) — no single AI failure crashes
component generation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Callable, Optional

from logger import Logger

from exceptions import (
    MissingComponentNameError,
    InvalidDesignTokensError,
    InvalidLayoutSpecificationError,
    UnsupportedComponentTypeError,
    MalformedHierarchyError,
    ComponentValidationError,
    ComponentGenerationError,
)
from generator_model import generate_component_with_llm
from generator_validator import validate_generated_code

logger = logging.getLogger(__name__)

_TRACEABILITY_NAMESPACE = uuid.UUID("6f6e1e2a-7b3d-4c9a-9e3f-2b6d4c1a9f00")


def _new_trace_id() -> str:
    return f"trc-{uuid.uuid4().hex[:12]}"


def get_component_type(node: dict) -> Optional[str]:
    """Resolve a node's component type field.

    Real SRS-generated ComponentNode data uses 'component_type', but
    earlier/simplified layout specs (and some of our own tests) use
    'type'. Accepting both means callers don't need to reshape SRS
    output before passing it in.
    """
    return node.get("component_type") or node.get("type")


class _ReactNativeRenderer:
    """Generates React Native JSX and StyleSheet fragments for a layout node.

    This is the deterministic FALLBACK path, only used when the AI
    generation step (generator_model.py) fails or its output fails
    validation (generator_validator.py). Isolated from
    `ComponentGenerator` so additional target-framework fallback
    renderers could be introduced as siblings later.
    """

    _CONTAINER_ELEMENTS: dict[str, str] = {
        "Card": "View",
        "Navbar": "View",
        "Header": "View",
        "Footer": "View",
        "Container": "View",
        "Row": "View",
        "Column": "View",
        "ScrollView": "ScrollView",
        "Screen": "View",
    }

    _LEAF_TYPES = {"Button", "TextInput", "Image", "Avatar"}

    def __init__(self) -> None:
        self._leaf_builders: dict[str, Callable[[dict, str], str]] = {
            "Button": self._render_button,
            "TextInput": self._render_text_input,
            "Image": self._render_image,
            "Avatar": self._render_avatar,
        }

    def supported_types(self) -> set[str]:
        """Return the set of component types this renderer has an EXPLICIT
        rendering rule for. This is NOT the full list of types it can
        handle — see render_node()'s default-to-View behavior below."""
        return set(self._CONTAINER_ELEMENTS) | self._LEAF_TYPES

    def render_node(
        self,
        node: dict,
        style_registry: dict[str, dict],
        style_key: str,
        children_jsx: str,
    ) -> str:
        """Render a single layout node into a JSX fragment.

        Real SRS-generated trees contain many component_type values
        this renderer has no specific rule for (e.g. SafeAreaView,
        SearchBar, FlatList, ItemCard, FormField). Since this renderer
        is only ever used as a last-resort FALLBACK (the AI is the
        primary path and can render any type it's given), unknown
        types are rendered as a generic View wrapping their children
        instead of raising — the fallback's job is to never crash,
        not to be pixel-perfect.
        """
        component_type = get_component_type(node)

        if component_type in self._leaf_builders:
            return self._leaf_builders[component_type](node, style_key)

        return self._render_container(component_type, style_key, children_jsx)

    def _render_container(self, component_type: str, style_key: str, children_jsx: str) -> str:
        """Render a container element (View/ScrollView) with nested children.
        Falls back to a plain View for any component_type without an
        explicit mapping (see render_node's docstring)."""
        tag = self._CONTAINER_ELEMENTS.get(component_type, "View")
        if children_jsx:
            return f"<{tag} style={{styles.{style_key}}}>\n{children_jsx}\n</{tag}>"
        return f"<{tag} style={{styles.{style_key}}} />"

    def _render_button(self, node: dict, style_key: str) -> str:
        """Render a Button as a TouchableOpacity wrapping a Text label."""
        label = self._escape(node.get("props", {}).get("label", "Button"))
        return (
            f"<TouchableOpacity style={{styles.{style_key}}}>\n"
            f'  <Text style={{styles.{style_key}_label}}>{label}</Text>\n'
            f"</TouchableOpacity>"
        )

    def _render_text_input(self, node: dict, style_key: str) -> str:
        """Render a TextInput with an optional placeholder prop."""
        placeholder = self._escape(node.get("props", {}).get("placeholder", ""))
        return f'<TextInput style={{styles.{style_key}}} placeholder="{placeholder}" />'

    def _render_image(self, node: dict, style_key: str) -> str:
        """Render an Image element sourced from a URI prop."""
        source_uri = self._escape(node.get("props", {}).get("source", ""))
        return f'<Image style={{styles.{style_key}}} source={{{{ uri: "{source_uri}" }}}} />'

    def _render_avatar(self, node: dict, style_key: str) -> str:
        """Render an Avatar as a circular Image element."""
        source_uri = self._escape(node.get("props", {}).get("source", ""))
        return f'<Image style={{styles.{style_key}}} source={{{{ uri: "{source_uri}" }}}} />'

    @staticmethod
    def _escape(value: str) -> str:
        """Escape double quotes so prop values do not break generated JSX."""
        return str(value).replace('"', '\\"')


class ComponentGenerator:
    """Generates reusable React Native component source code from an
    already-built Component Tree and design tokens.

    Primary path: sends the Component Tree + design tokens to an LLM
    (via generator_model.py) and validates the result
    (via generator_validator.py). Fallback path: if the AI call fails
    or its output doesn't pass validation, deterministically renders
    the tree using fixed Python rules instead — component generation
    never fails outright just because the AI is unavailable.
    """

    _SUPPORTED_ALIGNMENTS = {"start", "center", "end", "space-between", "space-around"}

    def __init__(self) -> None:
        self._renderer = _ReactNativeRenderer()

    def generate_component(
        self,
        component_name: str,
        design_tokens: dict,
        layout_spec: dict,
        tech_stack: Optional[dict] = None,
        trace_id: Optional[str] = None,
    ) -> str:
        """Generate production-ready React Native component source code.

        Args:
            component_name: The name to assign to the generated component.
            design_tokens: Design token values (colors, typography, spacing, etc.).
            layout_spec: The component tree (already built by the SRS module) —
                a node dict with `type`, `props`, `children`, etc.
            tech_stack: Optional tech-stack context (framework, state
                management, UI library) forwarded to the AI prompt.
            trace_id: Optional pipeline-wide trace ID for log correlation.
                Auto-generated if not provided.

        Returns:
            A formatted React Native component source string, tagged with a
            deterministic Traceability ID comment.
        """
        trace_id = trace_id or _new_trace_id()
        logger_instance = Logger(trace_id=trace_id)
        start_time = time.perf_counter()

        self._validate_inputs(component_name, design_tokens, layout_spec)

        traceability_id = self._generate_traceability_id(
            component_name, design_tokens, layout_spec
        )

        code = self._generate_with_ai_or_fallback(
            component_name, design_tokens, layout_spec, tech_stack, trace_id, logger_instance
        )

        final_code = self._attach_traceability_comment(code, traceability_id)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger_instance.log_event(
            "generator.py",
            f"Component generation complete | component={component_name} duration_ms={elapsed_ms:.2f}",
        )
        logger.info(
            "trace_id=%s | generator.py | stage=complete | component=%s duration_ms=%.2f",
            trace_id, component_name, elapsed_ms,
        )
        return final_code

    # ------------------------------------------------------------------
    # AI-first generation with deterministic fallback
    # ------------------------------------------------------------------

    def _generate_with_ai_or_fallback(
        self,
        component_name: str,
        design_tokens: dict,
        layout_spec: dict,
        tech_stack: Optional[dict],
        trace_id: str,
        logger_instance: Logger,
    ) -> str:
        """Try the AI generation path; fall back to rule-based rendering on failure."""
        ai_code = generate_component_with_llm(
            component_name, layout_spec, design_tokens, trace_id, tech_stack
        )

        if ai_code is not None:
            try:
                validate_generated_code(ai_code, component_name, trace_id)
                logger_instance.log_event(
                    "generator.py",
                    f"Using AI-generated code for component={component_name} (model path)",
                )
                logger.info(
                    "trace_id=%s | generator.py | using AI-generated code for component=%s (model path)",
                    trace_id, component_name,
                )
                return ai_code
            except ComponentValidationError as exc:
                logger_instance.log_event(
                    "generator.py",
                    f"AI output failed validation for component={component_name} | error={exc}",
                    level="WARNING",
                )
                logger.warning(
                    "trace_id=%s | generator.py | AI output failed validation for component=%s | error=%s",
                    trace_id, component_name, str(exc),
                )
                # fall through to rule-based path below

        logger_instance.log_event(
            "generator.py",
            f"AI path unavailable/failed for component={component_name}, falling back to rule-based renderer",
            level="WARNING",
        )
        logger.warning(
            "trace_id=%s | generator.py | AI path unavailable/failed for component=%s, falling back to rule-based renderer",
            trace_id, component_name,
        )

        try:
            fallback_code = self._render_with_rules(component_name, design_tokens, layout_spec)
            validate_generated_code(fallback_code, component_name, trace_id)
            return fallback_code
        except (UnsupportedComponentTypeError, MalformedHierarchyError):
            raise
        except ComponentValidationError as exc:
            logger_instance.log_event(
                "generator.py",
                f"Fallback rule-based output also failed validation for component={component_name} | error={exc}",
                level="CRITICAL",
            )
            logger.critical(
                "trace_id=%s | generator.py | fallback rule-based output also failed validation for component=%s | error=%s",
                trace_id, component_name, str(exc),
            )
            raise ComponentGenerationError(
                f"Both AI and rule-based fallback failed for component '{component_name}': {exc}"
            ) from exc
        except Exception as exc:
            raise ComponentGenerationError(
                f"Failed to generate component '{component_name}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_inputs(
        self, component_name: str, design_tokens: dict, layout_spec: dict
    ) -> None:
        """Run all input validation steps in sequence."""
        self._validate_component_name(component_name)
        self._validate_design_tokens(design_tokens)
        self._validate_layout_spec(layout_spec)

    @staticmethod
    def _validate_component_name(component_name: str) -> None:
        """Ensure the component name is present and a valid identifier-like string."""
        if not component_name or not component_name.strip():
            raise MissingComponentNameError("Component name must not be empty.")
        if not component_name[0].isalpha():
            raise MissingComponentNameError(
                f"Component name '{component_name}' must start with a letter."
            )

    @staticmethod
    def _validate_design_tokens(design_tokens: dict) -> None:
        """Ensure design tokens form a well-shaped dictionary."""
        if design_tokens is None or not isinstance(design_tokens, dict):
            raise InvalidDesignTokensError("Design tokens must be provided as a dictionary.")

    def _validate_layout_spec(self, layout_spec: dict, depth: int = 0) -> None:
        """Recursively validate the STRUCTURE of a layout specification.

        This intentionally does NOT reject unfamiliar component_type
        values (e.g. SafeAreaView, SearchBar, FlatList from real SRS
        output) — that check only matters for the rule-based fallback
        renderer, which now degrades unknown types to a generic View
        instead of crashing (see _ReactNativeRenderer.render_node).
        Structural validation just confirms the tree is well-formed
        enough to send to the AI and to walk recursively.
        """
        if layout_spec is None or not isinstance(layout_spec, dict):
            raise InvalidLayoutSpecificationError(
                "Layout specification must be provided as a dictionary."
            )

        component_type = get_component_type(layout_spec)
        if not component_type:
            raise InvalidLayoutSpecificationError(
                "Layout specification must include a 'type' or 'component_type' field."
            )

        alignment = layout_spec.get("alignment")
        if alignment is not None and alignment not in self._SUPPORTED_ALIGNMENTS:
            raise InvalidLayoutSpecificationError(
                f"Unsupported alignment value '{alignment}'."
            )

        children = layout_spec.get("children", [])
        if children is not None and not isinstance(children, list):
            raise MalformedHierarchyError("'children' must be a list of layout specifications.")

        if depth > 25:
            raise MalformedHierarchyError("Component hierarchy exceeds maximum nesting depth.")

        for child in children or []:
            self._validate_layout_spec(child, depth=depth + 1)

    # ------------------------------------------------------------------
    # Traceability
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_traceability_id(
        component_name: str, design_tokens: dict, layout_spec: dict
    ) -> str:
        """Deterministically derive a unique Traceability ID from the component inputs.

        Using UUIDv5 over a canonical JSON representation of the inputs
        guarantees the same inputs always yield the same ID (deterministic
        output) while distinct components remain distinguishable (uniqueness).
        """
        canonical_payload = json.dumps(
            {
                "component_name": component_name,
                "design_tokens": design_tokens,
                "layout_spec": layout_spec,
            },
            sort_keys=True,
            default=str,
        )
        digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
        return str(uuid.uuid5(_TRACEABILITY_NAMESPACE, digest))

    @staticmethod
    def _attach_traceability_comment(code: str, traceability_id: str) -> str:
        """Prefix generated code with a Traceability-ID comment, if not already present."""
        marker = f"// Traceability-ID: {traceability_id}"
        if traceability_id in code:
            return code
        return f"{marker}\n{code}"

    # ------------------------------------------------------------------
    # Rule-based fallback rendering (unchanged deterministic path)
    # ------------------------------------------------------------------

    def _render_with_rules(
        self, component_name: str, design_tokens: dict, layout_spec: dict
    ) -> str:
        """Deterministically render the component tree using fixed Python rules."""
        style_registry: dict[str, dict] = {}
        jsx_body = self._build_element(
            layout_spec, design_tokens, style_registry, style_key="root"
        )
        return self._render_component_source(
            component_name=component_name,
            jsx_body=jsx_body,
            style_registry=style_registry,
        )

    def _build_element(
        self,
        node: dict,
        design_tokens: dict,
        style_registry: dict[str, dict],
        style_key: str,
    ) -> str:
        """Recursively build JSX for a layout node and register its style entry."""
        style_registry[style_key] = self._apply_design_tokens(node, design_tokens)

        if get_component_type(node) == "Button":
            style_registry[f"{style_key}_label"] = self._build_label_style(design_tokens)

        children_jsx = ""
        children = node.get("children") or []
        rendered_children = [
            self._build_element(
                child, design_tokens, style_registry, style_key=f"{style_key}_{index}"
            )
            for index, child in enumerate(children)
        ]
        if rendered_children:
            children_jsx = "\n".join(self._indent(fragment) for fragment in rendered_children)

        return self._renderer.render_node(node, style_registry, style_key, children_jsx)

    def _apply_design_tokens(self, node: dict, design_tokens: dict) -> dict:
        """Merge design tokens and layout properties into a single style dictionary."""
        style: dict = {}
        component_type = get_component_type(node)

        spacing = design_tokens.get("spacing", {})
        style["padding"] = node.get("padding", spacing.get("default", 8) if isinstance(spacing, dict) else 8)
        if "margin" in node or "margin" in design_tokens:
            style["margin"] = node.get("margin", design_tokens.get("margin", 0))

        colors = design_tokens.get("colors", {}) if isinstance(design_tokens.get("colors"), dict) else {}

        # Interactive elements (buttons) are meant to stand out using the
        # user's chosen primary color, not blend into the background like
        # every other container. Without this distinction, a Button node
        # got the same white "surface" background as everything else,
        # which combined with its white ("onPrimary") label text made
        # every fallback-rendered button invisible — and meant the
        # primary/secondary/accent colors the user picked were never
        # actually applied anywhere in the rendered output.
        if component_type == "Button":
            style["backgroundColor"] = node.get(
                "backgroundColor", colors.get("primary", "#2563EB")
            )
        else:
            style["backgroundColor"] = node.get(
                "backgroundColor", colors.get("surface", "#FFFFFF")
            )

        if "borderRadius" in design_tokens or component_type == "Avatar":
            style["borderRadius"] = design_tokens.get(
                "borderRadius", 999 if component_type == "Avatar" else 4
            )

        elevation = design_tokens.get("elevation")
        if elevation is not None:
            style["elevation"] = elevation

        if "width" in node:
            style["width"] = node["width"]
        if "height" in node:
            style["height"] = node["height"]

        if component_type in {"Row", "Container", "Screen", "Card", "Navbar", "Header", "Footer"}:
            style["flexDirection"] = node.get("flexDirection", "row" if component_type == "Row" else "column")

        if component_type == "Column":
            style["flexDirection"] = "column"

        alignment = node.get("alignment")
        if alignment:
            style["justifyContent"] = alignment
            style["alignItems"] = "center"

        return style

    def _build_label_style(self, design_tokens: dict) -> dict:
        """Build a text-label style dictionary from typography design tokens."""
        typography = design_tokens.get("typography", {})
        colors = design_tokens.get("colors", {})
        return {
            "fontSize": typography.get("fontSize", 14) if isinstance(typography, dict) else 14,
            "fontWeight": typography.get("fontWeight", "500") if isinstance(typography, dict) else "500",
            "color": colors.get("onPrimary", "#FFFFFF") if isinstance(colors, dict) else "#FFFFFF",
        }

    def _render_component_source(
        self,
        component_name: str,
        jsx_body: str,
        style_registry: dict[str, dict],
    ) -> str:
        """Assemble the final React Native component file as a source string."""
        indented_jsx = self._indent(jsx_body, levels=2)
        styles_block = self._render_stylesheet(style_registry)

        return (
            f"import React from 'react';\n"
            f"import {{ View, Text, TouchableOpacity, TextInput, Image, ScrollView, StyleSheet }} "
            f"from 'react-native';\n\n"
            f"const {component_name} = () => {{\n"
            f"  return (\n"
            f"{indented_jsx}\n"
            f"  );\n"
            f"}};\n\n"
            f"{styles_block}\n\n"
            f"export default {component_name};\n"
        )

    @staticmethod
    def _render_stylesheet(style_registry: dict[str, dict]) -> str:
        """Render the collected style dictionaries into a StyleSheet.create() block."""
        entries = []
        for style_key, style_values in style_registry.items():
            formatted_values = ",\n".join(
                f"    {property_name}: {json.dumps(value)}"
                for property_name, value in style_values.items()
            )
            entries.append(f"  {style_key}: {{\n{formatted_values}\n  }}")

        joined_entries = ",\n".join(entries)
        return f"const styles = StyleSheet.create({{\n{joined_entries}\n}});"

    @staticmethod
    def _indent(text: str, levels: int = 1, spaces_per_level: int = 2) -> str:
        """Indent every line of the given text by the specified number of levels."""
        prefix = " " * (spaces_per_level * levels)
        return "\n".join(f"{prefix}{line}" for line in text.splitlines())