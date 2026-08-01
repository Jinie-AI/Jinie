"""
exceptions.py

Custom exceptions for backend/component_generator/. Every stage
(validation, AI generation, output validation, rule-based fallback)
raises from this shared vocabulary — same convention srs/ uses via
its own per-module exception classes.
"""

from __future__ import annotations


class ComponentGenerationError(Exception):
    """Base/generic exception for unrecoverable component-generation failures."""


class MissingComponentNameError(ComponentGenerationError):
    """Raised when `component_name` is missing, empty, or malformed."""


class InvalidDesignTokensError(ComponentGenerationError):
    """Raised when `design_tokens` is not a well-shaped dictionary."""


class InvalidLayoutSpecificationError(ComponentGenerationError):
    """Raised when the layout/component-tree specification is malformed."""


class UnsupportedComponentTypeError(ComponentGenerationError):
    """Raised when a node's `type`/`component_type` isn't recognized."""


class MalformedHierarchyError(ComponentGenerationError):
    """Raised when the component hierarchy (children) is malformed or too deep."""


class ComponentValidationError(ComponentGenerationError):
    """Raised when generated code fails post-generation validation checks."""