"""
generator_validator.py

Deterministic, rule-based safety net over AI-generated component code.
Contains no AI calls and no file I/O — pure checks against a string of
generated source. Kept separate from generator.py and generator_model.py
so validation rules can be tested and extended independently of how
the code was produced (AI or rule-based fallback).
"""

from __future__ import annotations

import logging

from .exceptions import ComponentValidationError

logger = logging.getLogger(__name__)

_REQUIRED_IMPORT_MARKER = "import"
_REQUIRED_EXPORT_MARKER = "export default"
_BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}"}


def validate_generated_code(code: str, component_name: str, trace_id: str) -> None:
    """
    Validate generated React Native component code. Raises
    ComponentValidationError on the first unrecoverable issue found;
    returns None (silently) if the code passes all checks.
    """
    _validate_not_empty(code, trace_id)
    _validate_has_imports(code, trace_id)
    _validate_has_default_export(code, trace_id)
    _validate_component_name_present(code, component_name, trace_id)
    _validate_balanced_brackets(code, trace_id)

    logger.info(
        "trace_id=%s | generator_validator.py | validation passed | component=%s",
        trace_id, component_name,
    )


def _validate_not_empty(code: str, trace_id: str) -> None:
    """Ensure the generated code is not missing or blank."""
    if not code or not code.strip():
        logger.warning(
            "trace_id=%s | generator_validator.py | validation failed | reason=empty_output",
            trace_id,
        )
        raise ComponentValidationError("Generated code is empty.")


def _validate_has_imports(code: str, trace_id: str) -> None:
    """Ensure at least one import statement is present."""
    if _REQUIRED_IMPORT_MARKER not in code:
        logger.warning(
            "trace_id=%s | generator_validator.py | validation failed | reason=missing_imports",
            trace_id,
        )
        raise ComponentValidationError("Generated code is missing import statements.")


def _validate_has_default_export(code: str, trace_id: str) -> None:
    """Ensure the component is actually exported."""
    if _REQUIRED_EXPORT_MARKER not in code:
        logger.warning(
            "trace_id=%s | generator_validator.py | validation failed | reason=missing_default_export",
            trace_id,
        )
        raise ComponentValidationError("Generated code is missing a default export.")


def _validate_component_name_present(code: str, component_name: str, trace_id: str) -> None:
    """Ensure the AI actually used the requested component name, not a made-up one."""
    if component_name not in code:
        logger.warning(
            "trace_id=%s | generator_validator.py | validation failed | reason=component_name_mismatch",
            trace_id,
        )
        raise ComponentValidationError(
            f"Generated code does not reference the requested component name '{component_name}'."
        )


def _validate_balanced_brackets(code: str, trace_id: str) -> None:
    """Ensure parentheses/brackets/braces are balanced (cheap structural sanity check)."""
    stack: list[str] = []

    for character in code:
        if character in _BRACKET_PAIRS:
            stack.append(_BRACKET_PAIRS[character])
        elif character in _BRACKET_PAIRS.values():
            if not stack or stack.pop() != character:
                logger.warning(
                    "trace_id=%s | generator_validator.py | validation failed | reason=unbalanced_brackets",
                    trace_id,
                )
                raise ComponentValidationError("Generated code has unbalanced brackets/braces.")

    if stack:
        logger.warning(
            "trace_id=%s | generator_validator.py | validation failed | reason=unbalanced_brackets",
            trace_id,
        )
        raise ComponentValidationError("Generated code has unbalanced brackets/braces.")