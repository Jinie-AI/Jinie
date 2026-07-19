from abc import ABC, abstractmethod
from typing import List, Optional

from .types import (
    FormattingResult,
    ValidationResult,
    FormattingOptions,
    SupportedStyles,
)


class IReformatter(ABC):
    """
    Contract for the Reformatter utility.

    Defines WHAT formatting, styling, validation, and rule-management
    operations the module must expose. Implementation details are
    intentionally excluded.
    """

    @abstractmethod
    def format_text(
        self, content: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Reformat plain text content according to the given options."""
        raise NotImplementedError

    @abstractmethod
    def format_code(
        self, content: str, language: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Reformat source code content for the specified language."""
        raise NotImplementedError

    @abstractmethod
    def format_document(
        self, content: str, content_type: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Reformat a structured document of the given content type."""
        raise NotImplementedError

    @abstractmethod
    def apply_style(
        self, content: str, style_name: str
    ) -> FormattingResult:
        """Apply a named style or style guide to the given content."""
        raise NotImplementedError

    @abstractmethod
    def normalize_whitespace(self, content: str) -> FormattingResult:
        """Normalize whitespace, indentation, and blank-line usage in content."""
        raise NotImplementedError

    @abstractmethod
    def pretty_print(
        self, content: str, content_type: str, options: Optional[FormattingOptions] = None
    ) -> FormattingResult:
        """Produce a canonically formatted, human-readable version of the content."""
        raise NotImplementedError

    @abstractmethod
    def validate_format(
        self, content: str, content_type: str
    ) -> ValidationResult:
        """Validate whether content conforms to expected formatting rules."""
        raise NotImplementedError

    @abstractmethod
    def detect_formatting_issues(
        self, content: str, content_type: str
    ) -> ValidationResult:
        """Detect and report formatting issues within the given content."""
        raise NotImplementedError

    @abstractmethod
    def get_supported_styles(self) -> SupportedStyles:
        """Return the list of styles and content types supported for formatting."""
        raise NotImplementedError

    @abstractmethod
    def reset_formatting_rules(self) -> None:
        """Reset formatting rules and options to module defaults."""
        raise NotImplementedError