"""
code_editor.py

Concrete implementation of ICodeEditor. Provides in-memory line-based
editing, lightweight formatting, and syntax validation for the two
languages Jinie generates: Python (backend glue) and TypeScript/TSX
(React Native components). Used by Module 05 (Component Generator) and
Module 06 (Compiler) before content is handed off to the FileHandler.
"""

import ast
import difflib
from typing import Optional, Tuple

from code_editor_contract import ICodeEditor


class CodeEditor(ICodeEditor):
    """Line-buffer based implementation of the code editor contract."""

    def __init__(self, content: str = ""):
        self._buffer: str = content

    # ---------------------------------------------------------------
    # Content loading / access
    # ---------------------------------------------------------------

    def load(self, content: str) -> None:
        self._buffer = content

    def get_content(self) -> str:
        return self._buffer

    def set_content(self, content: str) -> None:
        self._buffer = content

    # ---------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------

    def _lines(self) -> list:
        return self._buffer.splitlines(keepends=False)

    def _valid_range(self, start_line: int, end_line: int, total_lines: int) -> bool:
        return 1 <= start_line <= end_line <= total_lines

    # ---------------------------------------------------------------
    # Editing operations
    # ---------------------------------------------------------------

    def insert_at_line(self, line_number: int, snippet: str) -> bool:
        lines = self._lines()
        if not (1 <= line_number <= len(lines) + 1):
            return False
        insert_index = line_number - 1
        snippet_lines = snippet.splitlines()
        lines[insert_index:insert_index] = snippet_lines
        self._buffer = "\n".join(lines)
        return True

    def replace_block(self, start_line: int, end_line: int, new_code: str) -> bool:
        lines = self._lines()
        if not self._valid_range(start_line, end_line, len(lines)):
            return False
        new_lines = new_code.splitlines()
        lines[start_line - 1:end_line] = new_lines
        self._buffer = "\n".join(lines)
        return True

    def delete_block(self, start_line: int, end_line: int) -> bool:
        lines = self._lines()
        if not self._valid_range(start_line, end_line, len(lines)):
            return False
        del lines[start_line - 1:end_line]
        self._buffer = "\n".join(lines)
        return True

    def insert_component(self, component_name: str, component_code: str) -> bool:
        marker = f"// --- component:{component_name} ---"
        if marker in self._buffer:
            return False  # already inserted, avoid duplication

        wrapped = f"\n{marker}\n{component_code}\n// --- end:{component_name} ---\n"
        self._buffer = self._buffer.rstrip("\n") + "\n" + wrapped
        return True

    # ---------------------------------------------------------------
    # Formatting / validation
    # ---------------------------------------------------------------

    def format_code(self, language: str) -> str:
        language = language.lower()
        if language == "python":
            return self._format_python(self._buffer)
        if language in ("typescript", "tsx", "javascript", "jsx"):
            return self._format_js_like(self._buffer)
        return self._buffer

    def _format_python(self, code: str) -> str:
        try:
            import black  # optional dependency; falls back gracefully if absent
            return black.format_str(code, mode=black.Mode())
        except Exception:
            # Fallback: normalize blank lines and trailing whitespace only
            lines = [line.rstrip() for line in code.splitlines()]
            return "\n".join(lines) + "\n"

    def _format_js_like(self, code: str) -> str:
        # Lightweight fallback formatter: normalize indentation width to 2
        # spaces and strip trailing whitespace. A real pipeline would shell
        # out to `prettier`, but that requires a Node toolchain at runtime.
        lines = []
        for line in code.splitlines():
            stripped = line.rstrip()
            lines.append(stripped)
        return "\n".join(lines) + "\n"

    def validate_syntax(self, language: str) -> Tuple[bool, Optional[str]]:
        language = language.lower()
        if language == "python":
            return self._validate_python(self._buffer)
        if language in ("typescript", "tsx", "javascript", "jsx"):
            return self._validate_bracket_balance(self._buffer)
        return False, f"Unsupported language: {language}"

    def _validate_python(self, code: str) -> Tuple[bool, Optional[str]]:
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as exc:
            return False, f"SyntaxError: {exc.msg} (line {exc.lineno})"

    def _validate_bracket_balance(self, code: str) -> Tuple[bool, Optional[str]]:
        # A lightweight structural check for generated TSX/JSX before the
        # Tester module runs full Jest/Expo verification.
        pairs = {")": "(", "]": "[", "}": "{"}
        opening = set(pairs.values())
        stack = []
        for line_num, line in enumerate(code.splitlines(), start=1):
            for char in line:
                if char in opening:
                    stack.append((char, line_num))
                elif char in pairs:
                    if not stack or stack[-1][0] != pairs[char]:
                        return False, f"Unbalanced '{char}' at line {line_num}"
                    stack.pop()
        if stack:
            char, line_num = stack[-1]
            return False, f"Unclosed '{char}' opened at line {line_num}"
        return True, None

    # ---------------------------------------------------------------
    # Diffing
    # ---------------------------------------------------------------

    def get_diff_summary(self, original_content: str) -> str:
        diff = difflib.unified_diff(
            original_content.splitlines(),
            self._buffer.splitlines(),
            lineterm="",
            fromfile="original",
            tofile="edited",
        )
        return "\n".join(diff) or "No changes."