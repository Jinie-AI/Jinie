"""
backend/utilities/file_handler/tests/test_file_handler.py
==========================================================
All tests for FileHandler — unit tests AND the pipeline
boundary test (FileHandler → CodeEditor) live here.

No separate integration folder.

Run:
    cd jinie
    python -m pytest backend/utilities/file_handler/tests/ -v
"""

import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from backend.utilities.file_handler.file_handler          import FileHandler
from backend.utilities.file_handler.file_handler_contract import (
    FilePayload, WriteReceipt, FileInfo, FileHandlerError,
)
from backend.utilities.code_editor.code_editor          import CodeEditor
from backend.utilities.code_editor.code_editor_contract import CodePayload


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def fh():
    return FileHandler()


@pytest.fixture
def dart_file(tmp_path):
    """
    A raw Dart file with Jinie placeholders —
    exactly what CodeT5 (Compiler / Module 06) produces.
    """
    content = (
        "import 'package:flutter/material.dart';\n"
        "\n"
        "// TODO: fill placeholders before export\n"
        "class __WIDGET_NAME__ extends StatelessWidget {\n"
        "  final String title;\n"
        "  final double price;\n"
        "\n"
        "  const __WIDGET_NAME__("
        "{required this.title, required this.price});\n"
        "\n"
        "  @override\n"
        "  Widget build(BuildContext context) {\n"
        "    return Card(\n"
        "      color: __PRIMARY_COLOR__,\n"
        "      child: Text('__CURRENCY__ - ' + title),\n"
        "    );\n"
        "  }\n"
        "}\n"
    )
    path = tmp_path / "product_card.dart"
    path.write_text(content, encoding="utf-8")
    return str(path), content


@pytest.fixture
def srs_file(tmp_path):
    """A Markdown SRS file the SRS Generator (Module 04) writes."""
    content = (
        "# SRS — __APP_NAME__\n\n"
        "## Functional Requirements\n\n"
        "FR-001 Show product listing page.\n"
        "FR-002 Support __CURRENCY__ payments.\n"
    )
    path = tmp_path / "srs.md"
    path.write_text(content, encoding="utf-8")
    return str(path), content


# ═══════════════════════════════════════════════════════════════
# 1. READ
# ═══════════════════════════════════════════════════════════════

class TestRead:

    def test_returns_file_payload_type(self, fh, dart_file):
        path, _ = dart_file
        assert isinstance(fh.read(path), FilePayload)

    def test_raw_content_matches_disk(self, fh, dart_file):
        path, content = dart_file
        assert fh.read(path).raw_content == content

    def test_extension_dart(self, fh, dart_file):
        path, _ = dart_file
        assert fh.read(path).extension == ".dart"

    def test_extension_md(self, fh, srs_file):
        path, _ = srs_file
        assert fh.read(path).extension == ".md"

    def test_encoding_always_utf8(self, fh, dart_file):
        path, _ = dart_file
        assert fh.read(path).encoding == "utf-8"

    def test_size_bytes_correct(self, fh, dart_file):
        path, content = dart_file
        assert fh.read(path).size_bytes == len(content.encode("utf-8"))

    def test_path_is_absolute(self, fh, dart_file):
        path, _ = dart_file
        assert os.path.isabs(fh.read(path).path)

    def test_trace_id_prefixed_FH(self, fh, dart_file):
        path, _ = dart_file
        assert fh.read(path).trace_id.startswith("FH-")

    def test_two_reads_produce_unique_trace_ids(self, fh, dart_file):
        path, _ = dart_file
        assert fh.read(path).trace_id != fh.read(path).trace_id

    def test_missing_file_raises_file_not_found(self, fh, tmp_path):
        with pytest.raises(FileHandlerError) as exc:
            fh.read(str(tmp_path / "ghost.dart"))
        assert exc.value.code == "FILE_NOT_FOUND"

    def test_empty_path_raises_invalid_path(self, fh):
        with pytest.raises(FileHandlerError) as exc:
            fh.read("")
        assert exc.value.code == "INVALID_PATH"

    def test_blank_path_raises_invalid_path(self, fh):
        with pytest.raises(FileHandlerError) as exc:
            fh.read("   ")
        assert exc.value.code == "INVALID_PATH"

    def test_log_records_read(self, fh, dart_file):
        path, _ = dart_file
        fh.read(path)
        assert fh.get_log()[0]["operation"] == "READ"

    def test_log_trace_id_starts_FH(self, fh, dart_file):
        path, _ = dart_file
        fh.read(path)
        assert fh.get_log()[0]["trace_id"].startswith("FH-")

    def test_log_records_extension(self, fh, dart_file):
        path, _ = dart_file
        fh.read(path)
        assert fh.get_log()[0]["extension"] == ".dart"


# ═══════════════════════════════════════════════════════════════
# 2. WRITE
# ═══════════════════════════════════════════════════════════════

class TestWrite:

    def test_creates_file_on_disk(self, fh, tmp_path):
        path = str(tmp_path / "main.dart")
        fh.write(path, "void main() => runApp(MyApp());")
        assert Path(path).exists()

    def test_content_on_disk_matches(self, fh, tmp_path):
        content = "void main() => runApp(MyApp());"
        path    = str(tmp_path / "main.dart")
        fh.write(path, content)
        assert Path(path).read_text(encoding="utf-8") == content

    def test_returns_write_receipt(self, fh, tmp_path):
        receipt = fh.write(str(tmp_path / "f.dart"), "class A {}")
        assert isinstance(receipt, WriteReceipt)
        assert receipt.success is True

    def test_trace_id_prefixed_FH(self, fh, tmp_path):
        receipt = fh.write(str(tmp_path / "f.dart"), "class A {}")
        assert receipt.trace_id.startswith("FH-")

    def test_bytes_written_correct(self, fh, tmp_path):
        content = "class ProductCard {}"
        receipt = fh.write(str(tmp_path / "f.dart"), content)
        assert receipt.bytes_written == len(content.encode("utf-8"))

    def test_overwrite_true_replaces_content(self, fh, tmp_path):
        path = str(tmp_path / "f.dart")
        fh.write(path, "v1")
        fh.write(path, "v2", overwrite=True)
        assert Path(path).read_text(encoding="utf-8") == "v2"

    def test_overwrite_false_raises_destination_exists(self, fh, tmp_path):
        path = str(tmp_path / "f.dart")
        fh.write(path, "v1")
        with pytest.raises(FileHandlerError) as exc:
            fh.write(path, "v2", overwrite=False)
        assert exc.value.code == "DESTINATION_EXISTS"

    def test_creates_nested_parent_dirs(self, fh, tmp_path):
        # Compiler writes to lib/screens/home/home_screen.dart
        path = str(tmp_path / "lib" / "screens" / "home" / "home_screen.dart")
        fh.write(path, "class HomeScreen {}")
        assert Path(path).exists()

    def test_overwritten_flag_true_when_replacing(self, fh, tmp_path):
        path = str(tmp_path / "f.dart")
        fh.write(path, "v1")
        receipt = fh.write(path, "v2")
        assert receipt.overwritten is True

    def test_overwritten_flag_false_for_new_file(self, fh, tmp_path):
        receipt = fh.write(str(tmp_path / "new.dart"), "class X {}")
        assert receipt.overwritten is False


# ═══════════════════════════════════════════════════════════════
# 3. APPEND
# ═══════════════════════════════════════════════════════════════

class TestAppend:

    def test_appends_to_existing_file(self, fh, tmp_path):
        path = str(tmp_path / "widgets.dart")
        fh.write(path, "class A {}\n")
        fh.append(path, "class B {}\n")
        assert Path(path).read_text(encoding="utf-8") == "class A {}\nclass B {}\n"

    def test_creates_file_if_absent(self, fh, tmp_path):
        path = str(tmp_path / "new.dart")
        fh.append(path, "class X {}")
        assert Path(path).read_text(encoding="utf-8") == "class X {}"

    def test_returns_write_receipt(self, fh, tmp_path):
        receipt = fh.append(str(tmp_path / "log.txt"), "event\n")
        assert isinstance(receipt, WriteReceipt)
        assert receipt.success is True

    def test_bytes_written_correct(self, fh, tmp_path):
        content = "appended"
        receipt = fh.append(str(tmp_path / "f.txt"), content)
        assert receipt.bytes_written == len(content.encode("utf-8"))


# ═══════════════════════════════════════════════════════════════
# 4. DELETE
# ═══════════════════════════════════════════════════════════════

class TestDelete:

    def test_deletes_existing_file(self, fh, tmp_path):
        path = str(tmp_path / "temp.dart")
        fh.write(path, "temp")
        assert fh.delete(path) is True
        assert not Path(path).exists()

    def test_returns_false_if_already_gone(self, fh, tmp_path):
        assert fh.delete(str(tmp_path / "ghost.dart")) is False

    def test_log_records_delete(self, fh, tmp_path):
        path = str(tmp_path / "f.dart")
        fh.write(path, "x")
        fh.delete(path)
        ops = [e["operation"] for e in fh.get_log()]
        assert "DELETE" in ops


# ═══════════════════════════════════════════════════════════════
# 5. MOVE AND COPY
# ═══════════════════════════════════════════════════════════════

class TestMoveAndCopy:

    def test_move_relocates_file(self, fh, tmp_path):
        src = str(tmp_path / "src.dart")
        dst = str(tmp_path / "dst.dart")
        fh.write(src, "class A {}")
        new_path = fh.move(src, dst)
        assert not Path(src).exists()
        assert Path(new_path).read_text(encoding="utf-8") == "class A {}"

    def test_move_returns_absolute_path(self, fh, tmp_path):
        src = str(tmp_path / "a.dart")
        dst = str(tmp_path / "b.dart")
        fh.write(src, "x")
        assert os.path.isabs(fh.move(src, dst))

    def test_move_missing_source_raises_file_not_found(self, fh, tmp_path):
        with pytest.raises(FileHandlerError) as exc:
            fh.move(str(tmp_path / "no.dart"), str(tmp_path / "dst.dart"))
        assert exc.value.code == "FILE_NOT_FOUND"

    def test_copy_duplicates_file(self, fh, tmp_path):
        src = str(tmp_path / "template.dart")
        dst = str(tmp_path / "screen.dart")
        fh.write(src, "class Template {}")
        fh.copy(src, dst)
        assert Path(src).exists()
        assert Path(dst).read_text(encoding="utf-8") == "class Template {}"

    def test_copy_missing_source_raises_file_not_found(self, fh, tmp_path):
        with pytest.raises(FileHandlerError) as exc:
            fh.copy(str(tmp_path / "no.dart"), str(tmp_path / "dst.dart"))
        assert exc.value.code == "FILE_NOT_FOUND"


# ═══════════════════════════════════════════════════════════════
# 6. EXISTS AND LIST_DIR
# ═══════════════════════════════════════════════════════════════

class TestExistsAndListDir:

    def test_exists_true_for_real_file(self, fh, dart_file):
        path, _ = dart_file
        assert fh.exists(path) is True

    def test_exists_false_for_missing(self, fh, tmp_path):
        assert fh.exists(str(tmp_path / "nope.dart")) is False

    def test_list_dir_returns_file_info_objects(self, fh, tmp_path):
        fh.write(str(tmp_path / "a.dart"), "")
        entries = fh.list_dir(str(tmp_path))
        assert all(isinstance(e, FileInfo) for e in entries)

    def test_list_dir_sorted_alphabetically(self, fh, tmp_path):
        fh.write(str(tmp_path / "z.dart"), "")
        fh.write(str(tmp_path / "a.dart"), "")
        names = [e.name for e in fh.list_dir(str(tmp_path))]
        assert names == sorted(names, key=str.lower)

    def test_list_dir_extension_correct(self, fh, tmp_path):
        fh.write(str(tmp_path / "widget.dart"), "")
        entry = next(e for e in fh.list_dir(str(tmp_path))
                     if e.name == "widget.dart")
        assert entry.extension == ".dart"

    def test_list_dir_missing_raises_directory_not_found(self, fh, tmp_path):
        with pytest.raises(FileHandlerError) as exc:
            fh.list_dir(str(tmp_path / "missing_dir"))
        assert exc.value.code == "DIRECTORY_NOT_FOUND"

    def test_list_dir_marks_subdirs(self, fh, tmp_path):
        sub = tmp_path / "lib"
        sub.mkdir()
        entries  = fh.list_dir(str(tmp_path))
        lib_entry = next(e for e in entries if e.name == "lib")
        assert lib_entry.is_directory is True


# ═══════════════════════════════════════════════════════════════
# 7. PIPELINE BOUNDARY — FileHandler → CodeEditor
#    These tests belong here because they test the contract
#    that FileHandler's output is the correct input for CodeEditor.
#    No separate integration folder needed.
# ═══════════════════════════════════════════════════════════════

class TestPipelineBoundary:

    def test_file_payload_accepted_by_code_editor(self, fh, dart_file):
        """
        FilePayload from FileHandler.read() must be accepted
        by CodeEditor.load_file() without any transformation.
        """
        path, _ = dart_file
        fp = fh.read(path)
        ce = CodeEditor()
        ce.load_file(fp)          # must not raise
        assert ce.line_count > 0

    def test_traceability_chain_is_intact(self, fh, dart_file):
        """
        CodePayload.source_trace_id must equal FilePayload.trace_id.
        Module 03 (Traceability Manager) walks this chain.
        """
        path, _ = dart_file
        fp = fh.read(path)
        cp = CodeEditor().load_file(fp).get_payload()
        assert cp.source_trace_id == fp.trace_id

    def test_write_then_read_is_lossless(self, fh, tmp_path):
        """
        Compiler writes Dart code → FileHandler.write.
        FileHandler.read must return identical content.
        Any data loss here breaks the whole pipeline.
        """
        dart_code = (
            "class HomeScreen extends StatelessWidget {\n"
            "  @override\n"
            "  Widget build(BuildContext context) => Scaffold();\n"
            "}\n"
        )
        path = str(tmp_path / "home_screen.dart")
        fh.write(path, dart_code)
        fp = fh.read(path)
        assert fp.raw_content == dart_code

    def test_code_payload_has_correct_language_for_dart(self, fh, dart_file):
        """
        MdConverter uses CodePayload.language for the fenced code block tag.
        Must be 'dart' for Flutter files.
        """
        path, _ = dart_file
        cp = CodeEditor().load_file(fh.read(path)).get_payload()
        assert cp.language == "dart"

    def test_code_payload_has_correct_language_for_md(self, fh, srs_file):
        """SRS Markdown files must produce language='markdown'."""
        path, _ = srs_file
        cp = CodeEditor().load_file(fh.read(path)).get_payload()
        assert cp.language == "markdown"

    def test_full_compiler_chain_placeholders_replaced(self, fh, dart_file):
        """
        Full chain: FileHandler reads a CodeT5-generated Dart file,
        CodeEditor replaces all Jinie placeholders,
        resulting CodePayload has real values ready for MdConverter.
        """
        path, _ = dart_file
        fp = fh.read(path)

        cp = (
            CodeEditor()
            .load_file(fp)
            .delete_lines(3, 3)                                    # remove TODO
            .insert_lines(0, ["// Generated by Jinie v1.0"])       # add header
            .replace_token("__WIDGET_NAME__",  "ProductCard")      # class name
            .replace_token("__PRIMARY_COLOR__","Color(0xFF1A73E8)")# color
            .replace_token("__CURRENCY__",     "PKR")              # currency
            .get_payload()
        )

        assert isinstance(cp, CodePayload)

        # MdConverter fields must be populated
        assert cp.edited_content
        assert cp.language    == "dart"
        assert cp.source_path and os.path.isabs(cp.source_path)
        assert cp.trace_id.startswith("CE-")

        # All placeholders replaced
        assert "ProductCard"        in cp.edited_content
        assert "Color(0xFF1A73E8)"  in cp.edited_content
        assert "PKR"                in cp.edited_content
        assert "__WIDGET_NAME__"    not in cp.edited_content
        assert "__PRIMARY_COLOR__"  not in cp.edited_content
        assert "__CURRENCY__"       not in cp.edited_content

        # TODO comment removed
        assert "TODO" not in cp.edited_content

        # Jinie header inserted
        assert "Generated by Jinie" in cp.edited_content

        # Original preserved for audit
        assert "__WIDGET_NAME__" in cp.original_content

        # Edit history in correct order
        ops = [r.operation for r in cp.edit_history]
        assert ops == ["DELETE", "INSERT", "REPLACE_TOKEN",
                       "REPLACE_TOKEN", "REPLACE_TOKEN"]

    def test_two_files_have_independent_trace_chains(self, fh, tmp_path):
        """
        Compiler generates two Dart files.
        Each must have its own independent trace chain.
        """
        path_a = str(tmp_path / "screen_a.dart")
        path_b = str(tmp_path / "screen_b.dart")
        fh.write(path_a, "class ScreenA {}\n")
        fh.write(path_b, "class ScreenB {}\n")

        cp_a = CodeEditor().load_file(fh.read(path_a)).get_payload()
        cp_b = CodeEditor().load_file(fh.read(path_b)).get_payload()

        assert "ScreenA" in cp_a.edited_content
        assert "ScreenB" in cp_b.edited_content
        assert cp_a.trace_id        != cp_b.trace_id
        assert cp_a.source_trace_id != cp_b.source_trace_id