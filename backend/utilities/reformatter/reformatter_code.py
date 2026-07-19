from __future__ import annotations

import json
import re
import textwrap
from abc import ABC, abstractmethod
from typing import Optional
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from .reformatter_interface import IReformatter
from .types import (
    FormattingResult,
    ValidationResult,
    FormattingOptions,
    SupportedStyles,
)
from .exceptions import (
    EmptyContentError,
    InvalidFormattingOptionsError,
    UnsupportedContentTypeError,
    InvalidJSONError,
    InvalidXMLError,
    FormattingFailedError,
)


class _FormattingStrategy(ABC):
    """Defines the contract every content-type-specific formatting strategy must satisfy."""

    @abstractmethod
    def format(self, content: str, options: Optional[FormattingOptions]) -> str:
        """Return a reformatted version of the given content."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, content: str) -> tuple[bool, list[str], list[str]]:
        """Return (is_valid, errors, warnings) for the given content."""
        raise NotImplementedError

    @abstractmethod
    def detect_issues(self, content: str) -> list[str]:
        """Return a list of non-fatal formatting issues found in the content."""
        raise NotImplementedError


class _WhitespaceMixin:
    """Shared whitespace-normalization behavior reused across strategies."""

    @staticmethod
    def normalize(content: str, collapse_blank_lines: bool = True) -> str:
        """Strip trailing whitespace per line and collapse excess blank lines."""
        lines = [line.rstrip() for line in content.splitlines()]
        normalized = "\n".join(lines).strip("\n")
        if collapse_blank_lines:
            normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized + "\n"


class _PlainTextStrategy(_FormattingStrategy, _WhitespaceMixin):
    """Formatting strategy for unstructured plain text."""

    _DEFAULT_LINE_WIDTH = 80

    def format(self, content: str, options: Optional[FormattingOptions]) -> str:
        line_width = getattr(options, "line_width", self._DEFAULT_LINE_WIDTH) or self._DEFAULT_LINE_WIDTH
        normalized = self.normalize(content)

        wrapped_paragraphs = []
        for paragraph in normalized.split("\n\n"):
            if not paragraph.strip():
                continue
            wrapped = textwrap.fill(" ".join(paragraph.split()), width=line_width)
            wrapped_paragraphs.append(wrapped)

        return "\n\n".join(wrapped_paragraphs) + "\n"

    def validate(self, content: str) -> tuple[bool, list[str], list[str]]:
        return True, [], []

    def detect_issues(self, content: str) -> list[str]:
        issues = []
        for index, line in enumerate(content.splitlines(), start=1):
            if line != line.rstrip():
                issues.append(f"Line {index}: trailing whitespace detected.")
        return issues


class _MarkdownStrategy(_FormattingStrategy, _WhitespaceMixin):
    """Formatting strategy for Markdown content."""

    _UNORDERED_BULLET_PATTERN = re.compile(r"^(\s*)[-*+]\s+", re.MULTILINE)
    _FENCE_PATTERN = re.compile(r"^```", re.MULTILINE)
    _HEADING_PATTERN = re.compile(r"^(#{1,6})\s+")

    def format(self, content: str, options: Optional[FormattingOptions]) -> str:
        bullet_style = getattr(options, "bullet_style", "-") or "-"
        normalized = self.normalize(content)

        def replace_bullet(match: re.Match) -> str:
            return f"{match.group(1)}{bullet_style} "

        return self._UNORDERED_BULLET_PATTERN.sub(replace_bullet, normalized)

    def validate(self, content: str) -> tuple[bool, list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        fence_count = len(self._FENCE_PATTERN.findall(content))
        if fence_count % 2 != 0:
            errors.append("Unbalanced code fence (```) detected.")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def detect_issues(self, content: str) -> list[str]:
        issues = []
        for index, line in enumerate(content.splitlines(), start=1):
            heading_match = self._HEADING_PATTERN.match(line)
            if heading_match and not line[heading_match.end():].strip():
                issues.append(f"Line {index}: empty heading detected.")
        return issues


class _SourceCodeStrategy(_FormattingStrategy, _WhitespaceMixin):
    """Formatting strategy for source code (layout-only, language-agnostic).

    Only whitespace, indentation, and line-ending normalization are applied.
    No parsing, execution, or language-specific rewriting is performed.
    """

    _DEFAULT_INDENT_SIZE = 4
    _TAB_PATTERN = re.compile(r"\t")

    def format(self, content: str, options: Optional[FormattingOptions]) -> str:
        indent_options = getattr(options, "indentation", None)
        indent_size = getattr(indent_options, "size", self._DEFAULT_INDENT_SIZE) or self._DEFAULT_INDENT_SIZE
        indent_style = getattr(indent_options, "style", "spaces") or "spaces"

        normalized = self.normalize(content, collapse_blank_lines=False)

        if indent_style == "spaces":
            normalized = self._TAB_PATTERN.sub(" " * indent_size, normalized)

        return normalized

    def validate(self, content: str) -> tuple[bool, list[str], list[str]]:
        errors: list[str] = []
        pairs = {"(": ")", "[": "]", "{": "}"}
        stack: list[str] = []

        for character in content:
            if character in pairs:
                stack.append(pairs[character])
            elif character in pairs.values():
                if not stack or stack.pop() != character:
                    errors.append("Unbalanced brackets/braces detected.")
                    break

        if stack:
            errors.append("Unbalanced brackets/braces detected.")

        is_valid = len(errors) == 0
        return is_valid, errors, []

    def detect_issues(self, content: str) -> list[str]:
        issues = []
        has_tabs = "\t" in content
        has_leading_spaces_indent = re.search(r"^\x20+\S", content, re.MULTILINE) is not None
        if has_tabs and has_leading_spaces_indent:
            issues.append("Mixed tabs and spaces used for indentation.")

        for index, line in enumerate(content.splitlines(), start=1):
            if line != line.rstrip():
                issues.append(f"Line {index}: trailing whitespace detected.")
        return issues


class _JsonStrategy(_FormattingStrategy):
    """Formatting strategy for JSON content."""

    _DEFAULT_INDENT = 2

    def format(self, content: str, options: Optional[FormattingOptions]) -> str:
        parsed = self._parse(content)

        compact = getattr(options, "compact", False)
        sort_keys = getattr(options, "sort_keys", False)
        indent_options = getattr(options, "indentation", None)
        indent_size = getattr(indent_options, "size", self._DEFAULT_INDENT) or self._DEFAULT_INDENT

        if compact:
            return json.dumps(parsed, separators=(",", ":"), sort_keys=sort_keys)

        return json.dumps(parsed, indent=indent_size, sort_keys=sort_keys) + "\n"

    def validate(self, content: str) -> tuple[bool, list[str], list[str]]:
        try:
            self._parse(content)
        except InvalidJSONError as exc:
            return False, [str(exc)], []
        return True, [], []

    def detect_issues(self, content: str) -> list[str]:
        issues = []
        if "\t" in content:
            issues.append("Tab characters detected in JSON content.")
        return issues

    @staticmethod
    def _parse(content: str) -> object:
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise InvalidJSONError(f"Invalid JSON content: {exc}") from exc


class _XmlStrategy(_FormattingStrategy):
    """Formatting strategy for XML content."""

    _DEFAULT_INDENT = 2
    _BLANK_LINE_PATTERN = re.compile(r"\n\s*\n")

    def format(self, content: str, options: Optional[FormattingOptions]) -> str:
        document = self._parse(content)

        indent_options = getattr(options, "indentation", None)
        indent_size = getattr(indent_options, "size", self._DEFAULT_INDENT) or self._DEFAULT_INDENT
        indent = " " * indent_size

        pretty = document.toprettyxml(indent=indent)
        cleaned = self._BLANK_LINE_PATTERN.sub("\n", pretty)
        return cleaned.strip() + "\n"

    def validate(self, content: str) -> tuple[bool, list[str], list[str]]:
        try:
            self._parse(content)
        except InvalidXMLError as exc:
            return False, [str(exc)], []
        return True, [], []

    def detect_issues(self, content: str) -> list[str]:
        issues = []
        if "\t" in content:
            issues.append("Tab characters detected in XML content.")
        return issues

    @staticmethod
    def _parse(content: str) -> minidom.Document:
        try:
            return minidom.parseString(content)
        except ExpatError as exc:
            raise InvalidXMLError(f"Invalid XML content: {exc}") from exc


class Reformatter(IReformatter):
    """Concrete implementation of the Reformatter contract.

    Restructures and normalizes existing content without altering its
    semantic meaning. Delegates content-type-specific behavior to
    interchangeable formatting strategies, keeping the module open to
    extension (new content types) without modification of this class.
    """

    _STRATEGIES: dict[str, _FormattingStrategy] = {
        "plain_text": _PlainTextStrategy(),
        "markdown": _MarkdownStrategy(),
        "documentation": _MarkdownStrategy(),
        "source_code": _SourceCodeStrategy(),
        "json": _JsonStrategy(),
        "xml": _XmlStrategy(),
    }

    _STYLE_PRESETS: dict[str, dict] = {
        "compact": {"whitespace": "COLLAPSE", "compact": True},
        "expanded": {"whitespace": "PRESERVE", "compact": False},
        "standard": {"whitespace": "TRIM", "compact": False},
    }

    def __init__(self) -> None:
        self._active_options: Optional[FormattingOptions] = None

    def format_text(
        self, content: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Reformat plain text content according to the given options."""
        return self._run_formatting("plain_text", content, self._resolve_options(options))

    def format_code(
        self, content: str, language: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Reformat source code content for the specified language."""
        self._ensure_non_empty(language, "language")
        return self._run_formatting("source_code", content, self._resolve_options(options))

    def format_document(
        self, content: str, content_type: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Reformat a structured document of the given content type."""
        normalized_type = self._normalize_content_type(content_type)
        return self._run_formatting(normalized_type, content, self._resolve_options(options))

    def apply_style(self, content: str, style_name: str) -> FormattingResult:
        """Apply a named style or style guide to the given content."""
        self._ensure_non_empty(content, "content")
        preset = self._STYLE_PRESETS.get(style_name.strip().lower()) if style_name else None
        if preset is None:
            raise InvalidFormattingOptionsError(f"Unknown style '{style_name}'.")

        strategy = self._STRATEGIES["plain_text"]
        try:
            formatted = strategy.format(content, self._build_options_from_preset(preset))
        except Exception as exc:
            raise FormattingFailedError(f"Failed to apply style '{style_name}': {exc}") from exc

        return FormattingResult(
            success=True,
            content=formatted,
            content_type="plain_text",
            warnings=[],
            metadata={"style_applied": style_name.strip().lower()},
            error=None,
        )

    def normalize_whitespace(self, content: str) -> FormattingResult:
        """Normalize whitespace, indentation, and blank-line usage in content."""
        self._ensure_non_empty(content, "content")
        normalized = _WhitespaceMixin.normalize(content)

        return FormattingResult(
            success=True,
            content=normalized,
            content_type="plain_text",
            warnings=[],
            metadata={},
            error=None,
        )

    def pretty_print(
        self, content: str, content_type: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Produce a canonically formatted, human-readable version of the content."""
        normalized_type = self._normalize_content_type(content_type)
        return self._run_formatting(normalized_type, content, self._resolve_options(options))

    def validate_format(self, content: str, content_type: str) -> ValidationResult:
        """Validate whether content conforms to expected formatting rules."""
        normalized_type = self._normalize_content_type(content_type)
        if not content or not content.strip():
            return ValidationResult(is_valid=False, errors=["Content is empty."], warnings=[])

        strategy = self._STRATEGIES[normalized_type]
        is_valid, errors, warnings = strategy.validate(content)
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def detect_formatting_issues(self, content: str, content_type: str) -> ValidationResult:
        """Detect and report formatting issues within the given content."""
        normalized_type = self._normalize_content_type(content_type)
        if not content or not content.strip():
            return ValidationResult(is_valid=False, errors=["Content is empty."], warnings=[])

        strategy = self._STRATEGIES[normalized_type]
        issues = strategy.detect_issues(content)
        return ValidationResult(is_valid=len(issues) == 0, errors=[], warnings=issues)

    def get_supported_styles(self) -> SupportedStyles:
        """Return the list of styles and content types supported for formatting."""
        return SupportedStyles(
            content_types=list(self._STRATEGIES.keys()),
            style_names=list(self._STYLE_PRESETS.keys()),
        )

    def reset_formatting_rules(self) -> None:
        """Reset formatting rules and options to module defaults."""
        self._active_options = None

    def _run_formatting(
        self, content_type: str, content: str, options: Optional[FormattingOptions]
    ) -> FormattingResult:
        """Shared execution path for delegating a format request to its strategy."""
        self._ensure_non_empty(content, "content")
        strategy = self._STRATEGIES[content_type]

        try:
            formatted_content = strategy.format(content, options)
        except (InvalidJSONError, InvalidXMLError):
            raise
        except Exception as exc:
            raise FormattingFailedError(
                f"Formatting failed for content type '{content_type}': {exc}"
            ) from exc

        _, _, warnings = strategy.validate(formatted_content) if content_type in (
            "markdown", "documentation", "source_code"
        ) else (True, [], [])

        return FormattingResult(
            success=True,
            content=formatted_content,
            content_type=content_type,
            warnings=warnings,
            metadata={},
            error=None,
        )

    def _resolve_options(self, options: Optional[FormattingOptions]) -> Optional[FormattingOptions]:
        """Merge caller-supplied options with any active session defaults."""
        return options if options is not None else self._active_options

    @staticmethod
    def _build_options_from_preset(preset: dict) -> FormattingOptions:
        """Construct a FormattingOptions-compatible object from a preset dictionary."""
        return FormattingOptions(**preset)

    @staticmethod
    def _normalize_content_type(content_type: str) -> str:
        """Validate and normalize a content-type string against supported strategies."""
        if not content_type or not content_type.strip():
            raise UnsupportedContentTypeError("Content type must not be empty.")

        normalized = content_type.strip().lower()
        if normalized not in Reformatter._STRATEGIES:
            supported = ", ".join(Reformatter._STRATEGIES.keys())
            raise UnsupportedContentTypeError(
                f"Unsupported content type '{content_type}'. Supported: {supported}"
            )
        return normalized

    @staticmethod
    def _ensure_non_empty(value: str, field_name: str) -> None:
        """Raise an error if a required string value is missing or empty."""
        if value is None or not value.strip():
            raise EmptyContentError(f"'{field_name}' must not be empty.")