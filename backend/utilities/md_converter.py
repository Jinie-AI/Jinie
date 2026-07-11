from abc import ABC, abstractmethod
from typing import List, Optional

from .types import (
    ConversionResult,
    ValidationResult,
    ParsedDocument,
    FileOperationResult,
    ExportResult,
    ImportResult,
    SupportedFormats,
)


class IMarkdownConverter(ABC):
    """
    Contract for the Markdown Converter utility.

    Defines WHAT conversion, parsing, validation, and file/document
    operations the module must expose. Implementation details are
    intentionally excluded.
    """

    @abstractmethod
    def convert_markdown_to_html(
        self, content: str, options: Optional[dict] = None
    ) -> ConversionResult:
        """Convert Markdown content into HTML."""
        raise NotImplementedError

    @abstractmethod
    def convert_html_to_markdown(
        self, content: str, options: Optional[dict] = None
    ) -> ConversionResult:
        """Convert HTML content into Markdown."""
        raise NotImplementedError

    @abstractmethod
    def convert_markdown_to_text(
        self, content: str, options: Optional[dict] = None
    ) -> ConversionResult:
        """Convert Markdown content into plain text."""
        raise NotImplementedError

    @abstractmethod
    def parse_markdown(self, content: str) -> ParsedDocument:
        """Parse Markdown content into a structured document representation."""
        raise NotImplementedError

    @abstractmethod
    def validate_markdown(
        self, content: str, strict: bool = False
    ) -> ValidationResult:
        """Validate Markdown content against syntax and structural rules."""
        raise NotImplementedError

    @abstractmethod
    def read_markdown_file(self, file_path: str) -> FileOperationResult:
        """Read Markdown content from a file at the given path."""
        raise NotImplementedError

    @abstractmethod
    def write_markdown_file(
        self, file_path: str, content: str
    ) -> FileOperationResult:
        """Write Markdown content to a file at the given path."""
        raise NotImplementedError

    @abstractmethod
    def export_document(
        self, content: str, target_format: str, options: Optional[dict] = None
    ) -> ExportResult:
        """Export Markdown content into a specified target format."""
        raise NotImplementedError

    @abstractmethod
    def import_document(
        self, source_path: str, source_format: str
    ) -> ImportResult:
        """Import a document from a supported format into Markdown."""
        raise NotImplementedError

    @abstractmethod
    def get_supported_formats(self) -> SupportedFormats:
        """Return the list of formats supported for import, export, and conversion."""
        raise NotImplementedError