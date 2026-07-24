from __future__ import annotations

import hashlib
import json
import uuid
from typing import Callable, Optional

from .exceptions import (
    MissingComponentNameError,
    InvalidDesignTokensError,
    InvalidLayoutSpecificationError,
    UnsupportedComponentTypeError,
    MalformedHierarchyError,
    ComponentGenerationError,
)

_TRACEABILITY_NAMESPACE = uuid.UUID("6f6e1e2a-7b3d-4c9a-9e3f-2b6d4c1a9f00")


class _ReactNativeRenderer:
    """Generates React Native JSX and StyleSheet fragments for a layout node.

    Isolated from `ComponentGenerator` so that additional target-framework
    renderers (Flutter, React, Vue, Angular) can be introduced as siblings
    later without altering the public component-generation contract.
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
        """Return the full set of component types this renderer can produce."""
        return set(self._CONTAINER_ELEMENTS) | self._LEAF_TYPES

    def render_node(
        self,
        node: dict,
        style_registry: dict[str, dict],
        style_key: str,
        children_jsx: str,
    ) -> str:
        """Render a single layout node into a JSX fragment.

        `children_jsx` is pre-rendered by the caller for container types;
        leaf types ignore it since they do not accept nested children.
        """
        component_type = node["type"]

        if component_type in self._leaf_builders:
            return self._leaf_builders[component_type](node, style_key)

        return self._render_container(component_type, style_key, children_jsx)

    def _render_container(self, component_type: str, style_key: str, children_jsx: str) -> str:
        """Render a generic container element (View/ScrollView) with nested children."""
        tag = self._CONTAINER_ELEMENTS[component_type]
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
    """Generates reusable React Native component source code from design
    tokens and layout specifications.

    The public contract (`generate_component`) is fixed; internal rendering
    is delegated to a swappable renderer so that additional target
    frameworks can be supported later without changing this interface.
    """

    _SUPPORTED_ALIGNMENTS = {"start", "center", "end", "space-between", "space-around"}

    def __init__(self) -> None:
        self._renderer = _ReactNativeRenderer()

    def generate_component(
        self,
        component_name: str,
        design_tokens: dict,
        layout_spec: dict,
    ) -> str:
        """Generate a complete, deterministic React Native component as source code.

        Args:
            component_name: The name to assign to the generated component.
            design_tokens: Design token values (colors, typography, spacing, etc.).
            layout_spec: The component's layout/hierarchy specification.

        Returns:
            A formatted React Native component source string, tagged with a
            deterministic Traceability ID comment.
        """
        self._validate_inputs(component_name, design_tokens, layout_spec)

        traceability_id = self._generate_traceability_id(
            component_name, design_tokens, layout_spec
        )

        style_registry: dict[str, dict] = {}
        try:
            jsx_body = self._build_element(
                layout_spec, design_tokens, style_registry, style_key="root"
            )
        except (UnsupportedComponentTypeError, MalformedHierarchyError):
            raise
        except Exception as exc:
            raise ComponentGenerationError(
                f"Failed to generate component '{component_name}': {exc}"
            ) from exc

        return self._render_component_source(
            component_name=component_name,
            traceability_id=traceability_id,
            jsx_body=jsx_body,
            style_registry=style_registry,
        )

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
        """Recursively validate a layout specification and its child hierarchy."""
        if layout_spec is None or not isinstance(layout_spec, dict):
            raise InvalidLayoutSpecificationError(
                "Layout specification must be provided as a dictionary."
            )

        component_type = layout_spec.get("type")
        if not component_type:
            raise InvalidLayoutSpecificationError(
                "Layout specification must include a 'type' field."
            )
        if component_type not in self._renderer.supported_types():
            supported = ", ".join(sorted(self._renderer.supported_types()))
            raise UnsupportedComponentTypeError(
                f"Unsupported component type '{component_type}'. Supported: {supported}"
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

    # ------------------------------------------------------------------
    # Style & JSX generation
    # ------------------------------------------------------------------

    def _build_element(
        self,
        node: dict,
        design_tokens: dict,
        style_registry: dict[str, dict],
        style_key: str,
    ) -> str:
        """Recursively build JSX for a layout node and register its style entry."""
        style_registry[style_key] = self._apply_design_tokens(node, design_tokens)

        if node.get("type") == "Button":
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

        spacing = design_tokens.get("spacing", {})
        style["padding"] = node.get("padding", spacing.get("default", 8))
        if "margin" in node or "margin" in design_tokens:
            style["margin"] = node.get("margin", design_tokens.get("margin", 0))

        colors = design_tokens.get("colors", {})
        style["backgroundColor"] = node.get(
            "backgroundColor", colors.get("surface", "#FFFFFF")
        )

        if "borderRadius" in design_tokens or node.get("type") == "Avatar":
            style["borderRadius"] = design_tokens.get(
                "borderRadius", 999 if node.get("type") == "Avatar" else 4
            )

        elevation = design_tokens.get("elevation")
        if elevation is not None:
            style["elevation"] = elevation

        if "width" in node:
            style["width"] = node["width"]
        if "height" in node:
            style["height"] = node["height"]

        if node.get("type") in {"Row", "Container", "Screen", "Card", "Navbar", "Header", "Footer"}:
            style["flexDirection"] = node.get("flexDirection", "row" if node.get("type") == "Row" else "column")

        if node.get("type") == "Column":
            style["flexDirection"] = "column"

        alignment = node.get("alignment")
        if alignment:
            style["justifyContent"] = alignment
            style["alignItems"] = "center"

        return style

    def _build_label_style(self, design_tokens: dict) -> dict:
        """Build a text-label style dictionary from typography design tokens."""
        typography = design_tokens.get("typography", {})
        return {
            "fontSize": typography.get("fontSize", 14),
            "fontWeight": typography.get("fontWeight", "500"),
            "color": design_tokens.get("colors", {}).get("onPrimary", "#FFFFFF"),
        }

    def _render_component_source(
        self,
        component_name: str,
        traceability_id: str,
        jsx_body: str,
        style_registry: dict[str, dict],
    ) -> str:
        """Assemble the final React Native component file as a source string."""
        indented_jsx = self._indent(jsx_body, levels=2)
        styles_block = self._render_stylesheet(style_registry)

        return (
            f"// Traceability-ID: {traceability_id}\n"
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