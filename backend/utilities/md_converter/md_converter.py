from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

import markdown as _markdown_lib
from markdownify import markdownify as _html_to_markdown_lib

from .markdown_converter_interface import IMarkdownConverter
from .types import (
    ConversionResult,
    ValidationResult,
    ParsedDocument,
    FileOperationResult,
    ExportResult,
    ImportResult,
    SupportedFormats,
)
from .exceptions import (
    MarkdownFileNotFoundError,
    InvalidPathError,
    UnsupportedFormatError,
    EmptyDocumentError,
    InvalidMarkdownSyntaxError,
    MarkdownEncodingError,
    MarkdownPermissionError,
    ConversionFailedError,
)


class _MarkdownFileHandler:
    """Encapsulates all file-system access for Markdown content.

    Kept separate from conversion logic so that conversion methods
    remain independent of how content is sourced or persisted.
    """

    @staticmethod
    def read(file_path: str, encoding: str = "utf-8") -> str:
        """Read and return text content from a file path."""
        path = _MarkdownFileHandler._resolve_path(file_path)

        if not path.exists():
            raise MarkdownFileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise InvalidPathError(f"Path is not a file: {file_path}")

        try:
            content = path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            raise MarkdownEncodingError(
                f"Failed to decode file '{file_path}' using '{encoding}': {exc}"
            ) from exc
        except PermissionError as exc:
            raise MarkdownPermissionError(
                f"Permission denied reading file: {file_path}"
            ) from exc

        return content

    @staticmethod
    def write(file_path: str, content: str, encoding: str = "utf-8") -> Path:
        """Write text content to a file path, creating parent directories as needed."""
        path = _MarkdownFileHandler._resolve_path(file_path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)
        except PermissionError as exc:
            raise MarkdownPermissionError(
                f"Permission denied writing file: {file_path}"
            ) from exc
        except UnicodeEncodeError as exc:
            raise MarkdownEncodingError(
                f"Failed to encode content for file '{file_path}' using '{encoding}': {exc}"
            ) from exc

        return path

    @staticmethod
    def _resolve_path(file_path: str) -> Path:
        """Validate and resolve a raw path string into a Path object."""
        if not file_path or not file_path.strip():
            raise InvalidPathError("File path must not be empty.")
        try:
            return Path(file_path).expanduser().resolve()
        except (OSError, RuntimeError) as exc:
            raise InvalidPathError(f"Invalid file path '{file_path}': {exc}") from exc


class _PlainTextExtractor(HTMLParser):
    """Strips HTML tags from rendered Markdown to produce plain text."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def get_text(self) -> str:
        return "".join(self._chunks)


class _MarkdownValidator:
    """Performs syntax and structural validation of Markdown content."""

    _UNBALANCED_FENCE_PATTERN = re.compile(r"^```", re.MULTILINE)
    _MALFORMED_LINK_PATTERN = re.compile(r"\[[^\]]*\]\([^)]*$", re.MULTILINE)

    @classmethod
    def validate(cls, content: str, strict: bool = False) -> tuple[bool, list[str], list[str]]:
        """Validate content and return (is_valid, errors, warnings)."""
        errors: list[str] = []
        warnings: list[str] = []

        if not content or not content.strip():
            errors.append("Document is empty.")
            return False, errors, warnings

        fence_count = len(cls._UNBALANCED_FENCE_PATTERN.findall(content))
        if fence_count % 2 != 0:
            errors.append("Unbalanced code fence (```) detected.")

        if cls._MALFORMED_LINK_PATTERN.search(content):
            message = "Malformed or unterminated link syntax detected."
            if strict:
                errors.append(message)
            else:
                warnings.append(message)

        if "\t" in content and strict:
            warnings.append("Tab characters detected; spaces are recommended for indentation.")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings


class _MarkdownParser:
    """Parses Markdown content into a lightweight structural representation."""

    _HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
    _CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
    _LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    _IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    @classmethod
    def parse(cls, content: str) -> dict:
        """Extract headings, links, images, and code-block counts from content."""
        headings = [
            {"level": len(hashes), "text": text.strip()}
            for hashes, text in cls._HEADING_PATTERN.findall(content)
        ]
        code_blocks = cls._CODE_BLOCK_PATTERN.findall(content)
        images = cls._IMAGE_PATTERN.findall(content)
        links = [
            match for match in cls._LINK_PATTERN.findall(content)
            if match not in images
        ]

        return {
            "headings": headings,
            "code_block_count": len(code_blocks),
            "link_count": len(links),
            "image_count": len(images),
            "word_count": len(content.split()),
            "character_count": len(content),
        }


class _FormatConverter:
    """Performs the underlying content transformations between formats."""

    @staticmethod
    def markdown_to_html(content: str, options: Optional[dict] = None) -> str:
        """Render Markdown content into HTML using the `markdown` library."""
        extensions = (options or {}).get("extensions", ["extra", "tables", "fenced_code"])
        try:
            return _markdown_lib.markdown(content, extensions=extensions)
        except Exception as exc:
            raise ConversionFailedError(f"Markdown to HTML conversion failed: {exc}") from exc

    @staticmethod
    def html_to_markdown(content: str, options: Optional[dict] = None) -> str:
        """Convert HTML content into Markdown using `markdownify`."""
        heading_style = (options or {}).get("heading_style", "ATX")
        try:
            return _html_to_markdown_lib(content, heading_style=heading_style).strip()
        except Exception as exc:
            raise ConversionFailedError(f"HTML to Markdown conversion failed: {exc}") from exc

    @staticmethod
    def markdown_to_text(content: str, options: Optional[dict] = None) -> str:
        """Convert Markdown content into plain text by stripping rendered HTML tags."""
        try:
            html_content = _FormatConverter.markdown_to_html(content, options)
            extractor = _PlainTextExtractor()
            extractor.feed(html_content)
            text = extractor.get_text()
            return re.sub(r"\n{3,}", "\n\n", text).strip()
        except ConversionFailedError:
            raise
        except Exception as exc:
            raise ConversionFailedError(f"Markdown to text conversion failed: {exc}") from exc


class MarkdownConverter(IMarkdownConverter):
    """Concrete implementation of the Markdown Converter contract.

    Delegates file access, parsing, validation, and format conversion to
    dedicated private helpers, keeping each responsibility isolated and
    making it straightforward to extend with additional formats.
    """

    _SUPPORTED_IMPORT_FORMATS = ("markdown", "html")
    _SUPPORTED_EXPORT_FORMATS = ("html", "markdown", "text")

    def convert_markdown_to_html(
        self, content: str, options: Optional[dict] = None
    ) -> ConversionResult:
        """Convert Markdown content into HTML."""
        self._ensure_non_empty(content)
        html_output = _FormatConverter.markdown_to_html(content, options)
        return ConversionResult(
            success=True,
            content=html_output,
            source_format="markdown",
            target_format="html",
            metadata=_MarkdownParser.parse(content),
            error=None,
        )

    def convert_html_to_markdown(
        self, content: str, options: Optional[dict] = None
    ) -> ConversionResult:
        """Convert HTML content into Markdown."""
        self._ensure_non_empty(content)
        markdown_output = _FormatConverter.html_to_markdown(content, options)
        return ConversionResult(
            success=True,
            content=markdown_output,
            source_format="html",
            target_format="markdown",
            metadata=_MarkdownParser.parse(markdown_output),
            error=None,
        )

    def convert_markdown_to_text(
        self, content: str, options: Optional[dict] = None
    ) -> ConversionResult:
        """Convert Markdown content into plain text."""
        self._ensure_non_empty(content)
        text_output = _FormatConverter.markdown_to_text(content, options)
        return ConversionResult(
            success=True,
            content=text_output,
            source_format="markdown",
            target_format="text",
            metadata=_MarkdownParser.parse(content),
            error=None,
        )

    def parse_markdown(self, content: str) -> ParsedDocument:
        """Parse Markdown content into a structured document representation."""
        self._ensure_non_empty(content)
        structure = _MarkdownParser.parse(content)
        return ParsedDocument(
            raw_content=content,
            headings=structure["headings"],
            metadata={
                "code_block_count": structure["code_block_count"],
                "link_count": structure["link_count"],
                "image_count": structure["image_count"],
                "word_count": structure["word_count"],
                "character_count": structure["character_count"],
            },
        )

    def validate_markdown(
        self, content: str, strict: bool = False
    ) -> ValidationResult:
        """Validate Markdown content against syntax and structural rules."""
        if not content or not content.strip():
            return ValidationResult(is_valid=False, errors=["Document is empty."], warnings=[])

        is_valid, errors, warnings = _MarkdownValidator.validate(content, strict)
        if strict and not is_valid:
            raise InvalidMarkdownSyntaxError("; ".join(errors))

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def read_markdown_file(self, file_path: str) -> FileOperationResult:
        """Read Markdown content from a file at the given path."""
        content = _MarkdownFileHandler.read(file_path)
        self._ensure_non_empty(content)
        return FileOperationResult(success=True, path=file_path, content=content, error=None)

    def write_markdown_file(
        self, file_path: str, content: str
    ) -> FileOperationResult:
        """Write Markdown content to a file at the given path."""
        self._ensure_non_empty(content)
        resolved_path = _MarkdownFileHandler.write(file_path, content)
        return FileOperationResult(
            success=True, path=str(resolved_path), content=None, error=None
        )

    def export_document(
        self, content: str, target_format: str, options: Optional[dict] = None
    ) -> ExportResult:
        """Export Markdown content into a specified target format."""
        self._ensure_non_empty(content)
        normalized_format = self._normalize_format(target_format, self._SUPPORTED_EXPORT_FORMATS)

        converter_map = {
            "html": _FormatConverter.markdown_to_html,
            "text": _FormatConverter.markdown_to_text,
            "markdown": lambda c, o=None: c,
        }
        output_content = converter_map[normalized_format](content, options)

        return ExportResult(
            success=True,
            content=output_content,
            format=normalized_format,
            error=None,
        )

    def import_document(
        self, source_path: str, source_format: str
    ) -> ImportResult:
        """Import a document from a supported format into Markdown."""
        normalized_format = self._normalize_format(source_format, self._SUPPORTED_IMPORT_FORMATS)
        raw_content = _MarkdownFileHandler.read(source_path)
        self._ensure_non_empty(raw_content)

        if normalized_format == "html":
            markdown_content = _FormatConverter.html_to_markdown(raw_content)
        else:
            markdown_content = raw_content

        return ImportResult(
            success=True,
            content=markdown_content,
            source_format=normalized_format,
            error=None,
        )

    def get_supported_formats(self) -> SupportedFormats:
        """Return the list of formats supported for import, export, and conversion."""
        return SupportedFormats(
            import_formats=list(self._SUPPORTED_IMPORT_FORMATS),
            export_formats=list(self._SUPPORTED_EXPORT_FORMATS),
            conversion_pairs=[
                ("markdown", "html"),
                ("html", "markdown"),
                ("markdown", "text"),
            ],
        )

    @staticmethod
    def _ensure_non_empty(content: str) -> None:
        """Raise an error if content is missing or empty."""
        if content is None or not content.strip():
            raise EmptyDocumentError("Content must not be empty.")

    @staticmethod
    def _normalize_format(format_name: str, supported: tuple[str, ...]) -> str:
        """Validate and normalize a format string against a supported set."""
        if not format_name:
            raise UnsupportedFormatError("Format must not be empty.")

        normalized = format_name.strip().lower()
        if normalized not in supported:
            raise UnsupportedFormatError(
                f"Unsupported format '{format_name}'. Supported: {', '.join(supported)}"
            )
        return normalized