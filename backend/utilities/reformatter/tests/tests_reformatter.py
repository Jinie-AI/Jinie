import pytest

from .reformatter_impl import Reformatter
from .exceptions import (
    EmptyContentError,
    InvalidFormattingOptionsError,
    UnsupportedContentTypeError,
    InvalidJSONError,
    InvalidXMLError,
)


@pytest.fixture
def reformatter() -> Reformatter:
    return Reformatter()


@pytest.fixture
def messy_text() -> str:
    return "This   is  a line.   \n\n\n\nAnother line here.   \n"


@pytest.fixture
def messy_markdown() -> str:
    return "# Title   \n\n*  item one\n+  item two\n\n\n\nMore text.\n"


@pytest.fixture
def messy_code() -> str:
    return "def foo():\n\tprint('hi')   \n\treturn (1 + 2 \n"


@pytest.fixture
def valid_json_text() -> str:
    return '{"b": 2, "a": 1, "nested": {"z": true, "y": false}}'


@pytest.fixture
def valid_xml_text() -> str:
    return "<root><child>value</child><child2 attr=\"x\">text</child2></root>"


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

class TestFormatText:
    def test_formats_plain_text(self, reformatter, messy_text):
        result = reformatter.format_text(messy_text)

        assert result.success is True
        assert result.content_type == "plain_text"
        assert "\n\n\n" not in result.content
        assert result.content.endswith("\n")

    def test_raises_on_empty_content(self, reformatter):
        with pytest.raises(EmptyContentError):
            reformatter.format_text("")

    def test_raises_on_whitespace_only_content(self, reformatter):
        with pytest.raises(EmptyContentError):
            reformatter.format_text("   \n\t  ")


# ---------------------------------------------------------------------------
# format_code
# ---------------------------------------------------------------------------

class TestFormatCode:
    def test_formats_code_content(self, reformatter, messy_code):
        result = reformatter.format_code(messy_code, language="python")

        assert result.success is True
        assert result.content_type == "source_code"
        assert "\t" not in result.content

    def test_raises_on_empty_content(self, reformatter):
        with pytest.raises(EmptyContentError):
            reformatter.format_code("", language="python")

    def test_raises_on_empty_language(self, reformatter, messy_code):
        with pytest.raises(EmptyContentError):
            reformatter.format_code(messy_code, language="")


# ---------------------------------------------------------------------------
# format_document
# ---------------------------------------------------------------------------

class TestFormatDocument:
    def test_formats_markdown_document(self, reformatter, messy_markdown):
        result = reformatter.format_document(messy_markdown, "markdown")

        assert result.success is True
        assert result.content_type == "markdown"
        assert "* item one" not in result.content
        assert "- item one" in result.content
        assert "- item two" in result.content

    def test_formats_json_document(self, reformatter, valid_json_text):
        result = reformatter.format_document(valid_json_text, "json")

        assert result.success is True
        assert result.content_type == "json"
        assert '"a": 1' in result.content

    def test_formats_xml_document(self, reformatter, valid_xml_text):
        result = reformatter.format_document(valid_xml_text, "xml")

        assert result.success is True
        assert result.content_type == "xml"
        assert "<root>" in result.content

    def test_content_type_is_case_insensitive(self, reformatter, valid_json_text):
        result = reformatter.format_document(valid_json_text, "JSON")

        assert result.content_type == "json"

    def test_raises_on_unsupported_content_type(self, reformatter, messy_text):
        with pytest.raises(UnsupportedContentTypeError):
            reformatter.format_document(messy_text, "yaml")

    def test_raises_on_empty_content_type(self, reformatter, messy_text):
        with pytest.raises(UnsupportedContentTypeError):
            reformatter.format_document(messy_text, "")

    def test_raises_on_empty_content(self, reformatter):
        with pytest.raises(EmptyContentError):
            reformatter.format_document("", "markdown")

    def test_raises_invalid_json_error_on_malformed_json(self, reformatter):
        with pytest.raises(InvalidJSONError):
            reformatter.format_document("{not valid json", "json")

    def test_raises_invalid_xml_error_on_malformed_xml(self, reformatter):
        with pytest.raises(InvalidXMLError):
            reformatter.format_document("<root><unclosed></root>", "xml")


# ---------------------------------------------------------------------------
# apply_style
# ---------------------------------------------------------------------------

class TestApplyStyle:
    def test_applies_known_style(self, reformatter, messy_text):
        result = reformatter.apply_style(messy_text, "standard")

        assert result.success is True
        assert result.metadata["style_applied"] == "standard"

    def test_style_name_is_case_insensitive(self, reformatter, messy_text):
        result = reformatter.apply_style(messy_text, "COMPACT")

        assert result.metadata["style_applied"] == "compact"

    def test_raises_on_unknown_style(self, reformatter, messy_text):
        with pytest.raises(InvalidFormattingOptionsError):
            reformatter.apply_style(messy_text, "nonexistent_style")

    def test_raises_on_empty_content(self, reformatter):
        with pytest.raises(EmptyContentError):
            reformatter.apply_style("", "standard")


# ---------------------------------------------------------------------------
# normalize_whitespace
# ---------------------------------------------------------------------------

class TestNormalizeWhitespace:
    def test_strips_trailing_whitespace_and_collapses_blank_lines(self, reformatter, messy_text):
        result = reformatter.normalize_whitespace(messy_text)

        assert result.success is True
        for line in result.content.splitlines():
            assert line == line.rstrip()
        assert "\n\n\n" not in result.content

    def test_raises_on_empty_content(self, reformatter):
        with pytest.raises(EmptyContentError):
            reformatter.normalize_whitespace("")


# ---------------------------------------------------------------------------
# pretty_print
# ---------------------------------------------------------------------------

class TestPrettyPrint:
    def test_pretty_prints_json(self, reformatter, valid_json_text):
        result = reformatter.pretty_print(valid_json_text, "json")

        assert result.success is True
        assert "\n" in result.content

    def test_pretty_prints_xml(self, reformatter, valid_xml_text):
        result = reformatter.pretty_print(valid_xml_text, "xml")

        assert result.success is True
        assert "<child>" in result.content

    def test_raises_on_unsupported_content_type(self, reformatter, valid_json_text):
        with pytest.raises(UnsupportedContentTypeError):
            reformatter.pretty_print(valid_json_text, "sql")


# ---------------------------------------------------------------------------
# validate_format
# ---------------------------------------------------------------------------

class TestValidateFormat:
    def test_valid_json_passes(self, reformatter, valid_json_text):
        result = reformatter.validate_format(valid_json_text, "json")

        assert result.is_valid is True
        assert result.errors == []

    def test_invalid_json_fails(self, reformatter):
        result = reformatter.validate_format("{not valid json", "json")

        assert result.is_valid is False
        assert len(result.errors) >= 1

    def test_valid_xml_passes(self, reformatter, valid_xml_text):
        result = reformatter.validate_format(valid_xml_text, "xml")

        assert result.is_valid is True

    def test_invalid_xml_fails(self, reformatter):
        result = reformatter.validate_format("<root><unclosed></root>", "xml")

        assert result.is_valid is False
        assert len(result.errors) >= 1

    def test_unbalanced_markdown_fence_fails(self, reformatter):
        content = "# Title\n```python\nprint('hi')\n"
        result = reformatter.validate_format(content, "markdown")

        assert result.is_valid is False
        assert any("fence" in error.lower() for error in result.errors)

    def test_unbalanced_code_brackets_fail(self, reformatter):
        content = "def foo(:\n    return 1\n"
        result = reformatter.validate_format(content, "source_code")

        assert result.is_valid is False

    def test_empty_content_is_invalid(self, reformatter):
        result = reformatter.validate_format("", "plain_text")

        assert result.is_valid is False
        assert "empty" in result.errors[0].lower()

    def test_raises_on_unsupported_content_type(self, reformatter, valid_json_text):
        with pytest.raises(UnsupportedContentTypeError):
            reformatter.validate_format(valid_json_text, "docx")


# ---------------------------------------------------------------------------
# detect_formatting_issues
# ---------------------------------------------------------------------------

class TestDetectFormattingIssues:
    def test_detects_trailing_whitespace_in_text(self, reformatter, messy_text):
        result = reformatter.detect_formatting_issues(messy_text, "plain_text")

        assert result.is_valid is False
        assert any("trailing whitespace" in warning.lower() for warning in result.warnings)

    def test_detects_empty_markdown_heading(self, reformatter):
        content = "#\n\nSome text.\n"
        result = reformatter.detect_formatting_issues(content, "markdown")

        assert result.is_valid is False
        assert any("empty heading" in warning.lower() for warning in result.warnings)

    def test_clean_content_has_no_issues(self, reformatter):
        content = "# Title\n\nClean content with no issues.\n"
        result = reformatter.detect_formatting_issues(content, "markdown")

        assert result.is_valid is True
        assert result.warnings == []

    def test_raises_on_empty_content(self, reformatter):
        result = reformatter.detect_formatting_issues("", "plain_text")

        assert result.is_valid is False
        assert "empty" in result.errors[0].lower()

    def test_raises_on_unsupported_content_type(self, reformatter, messy_text):
        with pytest.raises(UnsupportedContentTypeError):
            reformatter.detect_formatting_issues(messy_text, "latex")


# ---------------------------------------------------------------------------
# get_supported_styles
# ---------------------------------------------------------------------------

class TestGetSupportedStyles:
    def test_returns_expected_content_types_and_styles(self, reformatter):
        styles = reformatter.get_supported_styles()

        assert "markdown" in styles.content_types
        assert "json" in styles.content_types
        assert "xml" in styles.content_types
        assert "source_code" in styles.content_types
        assert "standard" in styles.style_names
        assert "compact" in styles.style_names


# ---------------------------------------------------------------------------
# reset_formatting_rules
# ---------------------------------------------------------------------------

class TestResetFormattingRules:
    def test_reset_clears_active_options(self, reformatter):
        reformatter._active_options = object()

        result = reformatter.reset_formatting_rules()

        assert result is None
        assert reformatter._active_options is None