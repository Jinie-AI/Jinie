import stat
import sys

import pytest

from utilities.md_converter.md_converter import MarkdownConverter
from .exceptions import (
    MarkdownFileNotFoundError,
    InvalidPathError,
    UnsupportedFormatError,
    EmptyDocumentError,
    InvalidMarkdownSyntaxError,
    MarkdownPermissionError,
)


@pytest.fixture
def converter() -> MarkdownConverter:
    return MarkdownConverter()


@pytest.fixture
def sample_markdown() -> str:
    return (
        "# Title\n\n"
        "Some **bold** text with a [link](https://example.com) "
        "and an ![image](image.png).\n\n"
        "```python\nprint('hello')\n```\n"
    )


@pytest.fixture
def sample_html() -> str:
    return "<h1>Title</h1><p>Some <strong>bold</strong> text.</p>"


# ---------------------------------------------------------------------------
# convert_markdown_to_html
# ---------------------------------------------------------------------------

class TestConvertMarkdownToHtml:
    def test_converts_valid_markdown(self, converter, sample_markdown):
        result = converter.convert_markdown_to_html(sample_markdown)

        assert result.success is True
        assert "<h1>" in result.content
        assert result.source_format == "markdown"
        assert result.target_format == "html"

    def test_raises_on_empty_content(self, converter):
        with pytest.raises(EmptyDocumentError):
            converter.convert_markdown_to_html("")

    def test_raises_on_whitespace_only_content(self, converter):
        with pytest.raises(EmptyDocumentError):
            converter.convert_markdown_to_html("   \n\t  ")

    def test_metadata_reflects_structure(self, converter, sample_markdown):
        result = converter.convert_markdown_to_html(sample_markdown)

        assert result.metadata["link_count"] == 1
        assert result.metadata["image_count"] == 1
        assert result.metadata["code_block_count"] == 1


# ---------------------------------------------------------------------------
# convert_html_to_markdown
# ---------------------------------------------------------------------------

class TestConvertHtmlToMarkdown:
    def test_converts_valid_html(self, converter, sample_html):
        result = converter.convert_html_to_markdown(sample_html)

        assert result.success is True
        assert "Title" in result.content
        assert result.source_format == "html"
        assert result.target_format == "markdown"

    def test_raises_on_empty_content(self, converter):
        with pytest.raises(EmptyDocumentError):
            converter.convert_html_to_markdown("")


# ---------------------------------------------------------------------------
# convert_markdown_to_text
# ---------------------------------------------------------------------------

class TestConvertMarkdownToText:
    def test_strips_markup(self, converter, sample_markdown):
        result = converter.convert_markdown_to_text(sample_markdown)

        assert result.success is True
        assert "<" not in result.content
        assert "Title" in result.content

    def test_raises_on_empty_content(self, converter):
        with pytest.raises(EmptyDocumentError):
            converter.convert_markdown_to_text("")


# ---------------------------------------------------------------------------
# parse_markdown
# ---------------------------------------------------------------------------

class TestParseMarkdown:
    def test_extracts_headings(self, converter, sample_markdown):
        parsed = converter.parse_markdown(sample_markdown)

        assert parsed.headings == [{"level": 1, "text": "Title"}]
        assert parsed.raw_content == sample_markdown

    def test_metadata_counts(self, converter, sample_markdown):
        parsed = converter.parse_markdown(sample_markdown)

        assert parsed.metadata["link_count"] == 1
        assert parsed.metadata["image_count"] == 1
        assert parsed.metadata["code_block_count"] == 1
        assert parsed.metadata["word_count"] > 0

    def test_raises_on_empty_content(self, converter):
        with pytest.raises(EmptyDocumentError):
            converter.parse_markdown("")


# ---------------------------------------------------------------------------
# validate_markdown
# ---------------------------------------------------------------------------

class TestValidateMarkdown:
    def test_valid_markdown_passes(self, converter, sample_markdown):
        result = converter.validate_markdown(sample_markdown)

        assert result.is_valid is True
        assert result.errors == []

    def test_empty_markdown_is_invalid(self, converter):
        result = converter.validate_markdown("")

        assert result.is_valid is False
        assert "empty" in result.errors[0].lower()

    def test_unbalanced_code_fence_detected(self, converter):
        content = "# Title\n```python\nprint('hi')\n"
        result = converter.validate_markdown(content)

        assert result.is_valid is False
        assert any("fence" in error.lower() for error in result.errors)

    def test_strict_mode_raises_on_invalid_syntax(self, converter):
        content = "# Title\n```python\nprint('hi')\n"
        with pytest.raises(InvalidMarkdownSyntaxError):
            converter.validate_markdown(content, strict=True)

    def test_malformed_link_is_warning_in_non_strict_mode(self, converter):
        content = "# Title\n[broken link(missing-paren\n"
        result = converter.validate_markdown(content, strict=False)

        assert result.is_valid is True
        assert len(result.warnings) >= 1


# ---------------------------------------------------------------------------
# read_markdown_file / write_markdown_file
# ---------------------------------------------------------------------------

class TestFileOperations:
    def test_write_then_read_round_trip(self, converter, tmp_path, sample_markdown):
        file_path = tmp_path / "doc.md"

        write_result = converter.write_markdown_file(str(file_path), sample_markdown)
        assert write_result.success is True
        assert file_path.exists()

        read_result = converter.read_markdown_file(str(file_path))
        assert read_result.success is True
        assert read_result.content == sample_markdown

    def test_read_raises_on_missing_file(self, converter, tmp_path):
        missing_path = tmp_path / "does_not_exist.md"

        with pytest.raises(MarkdownFileNotFoundError):
            converter.read_markdown_file(str(missing_path))

    def test_read_raises_on_directory_path(self, converter, tmp_path):
        with pytest.raises(InvalidPathError):
            converter.read_markdown_file(str(tmp_path))

    def test_read_raises_on_empty_path(self, converter):
        with pytest.raises(InvalidPathError):
            converter.read_markdown_file("")

    def test_write_raises_on_empty_content(self, converter, tmp_path):
        file_path = tmp_path / "doc.md"
        with pytest.raises(EmptyDocumentError):
            converter.write_markdown_file(str(file_path), "")

    def test_write_creates_missing_parent_directories(self, converter, tmp_path, sample_markdown):
        nested_path = tmp_path / "nested" / "dir" / "doc.md"

        result = converter.write_markdown_file(str(nested_path), sample_markdown)

        assert result.success is True
        assert nested_path.exists()

    @pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason="POSIX permission bits are not enforced the same way on Windows.",
    )
    def test_read_raises_on_permission_denied(self, converter, tmp_path, sample_markdown):
        file_path = tmp_path / "locked.md"
        file_path.write_text(sample_markdown, encoding="utf-8")
        file_path.chmod(0)

        try:
            with pytest.raises(MarkdownPermissionError):
                converter.read_markdown_file(str(file_path))
        finally:
            file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)


# ---------------------------------------------------------------------------
# export_document
# ---------------------------------------------------------------------------

class TestExportDocument:
    def test_export_to_html(self, converter, sample_markdown):
        result = converter.export_document(sample_markdown, "html")

        assert result.success is True
        assert result.format == "html"
        assert "<h1>" in result.content

    def test_export_to_text(self, converter, sample_markdown):
        result = converter.export_document(sample_markdown, "text")

        assert result.success is True
        assert result.format == "text"
        assert "<" not in result.content

    def test_export_to_markdown_is_passthrough(self, converter, sample_markdown):
        result = converter.export_document(sample_markdown, "markdown")

        assert result.success is True
        assert result.content == sample_markdown

    def test_export_is_case_insensitive(self, converter, sample_markdown):
        result = converter.export_document(sample_markdown, "HTML")

        assert result.format == "html"

    def test_raises_on_unsupported_format(self, converter, sample_markdown):
        with pytest.raises(UnsupportedFormatError):
            converter.export_document(sample_markdown, "pdf")

    def test_raises_on_empty_content(self, converter):
        with pytest.raises(EmptyDocumentError):
            converter.export_document("", "html")


# ---------------------------------------------------------------------------
# import_document
# ---------------------------------------------------------------------------

class TestImportDocument:
    def test_import_markdown_file(self, converter, tmp_path, sample_markdown):
        file_path = tmp_path / "doc.md"
        file_path.write_text(sample_markdown, encoding="utf-8")

        result = converter.import_document(str(file_path), "markdown")

        assert result.success is True
        assert result.content == sample_markdown
        assert result.source_format == "markdown"

    def test_import_html_file_converts_to_markdown(self, converter, tmp_path, sample_html):
        file_path = tmp_path / "doc.html"
        file_path.write_text(sample_html, encoding="utf-8")

        result = converter.import_document(str(file_path), "html")

        assert result.success is True
        assert "Title" in result.content
        assert result.source_format == "html"

    def test_raises_on_unsupported_format(self, converter, tmp_path, sample_markdown):
        file_path = tmp_path / "doc.md"
        file_path.write_text(sample_markdown, encoding="utf-8")

        with pytest.raises(UnsupportedFormatError):
            converter.import_document(str(file_path), "docx")

    def test_raises_on_missing_file(self, converter, tmp_path):
        missing_path = tmp_path / "missing.md"

        with pytest.raises(MarkdownFileNotFoundError):
            converter.import_document(str(missing_path), "markdown")

    def test_raises_on_empty_source_file(self, converter, tmp_path):
        file_path = tmp_path / "empty.md"
        file_path.write_text("", encoding="utf-8")

        with pytest.raises(EmptyDocumentError):
            converter.import_document(str(file_path), "markdown")


# ---------------------------------------------------------------------------
# get_supported_formats
# ---------------------------------------------------------------------------

class TestGetSupportedFormats:
    def test_returns_expected_formats(self, converter):
        formats = converter.get_supported_formats()

        assert "markdown" in formats.import_formats
        assert "html" in formats.import_formats
        assert "html" in formats.export_formats
        assert "text" in formats.export_formats
        assert ("markdown", "html") in formats.conversion_pairs
        assert ("html", "markdown") in formats.conversion_pairs