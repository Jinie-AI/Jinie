"""
code_editor_contract.py

Contract (interface) for Module 01 — Utilities: Code Editor.

Defines the operations Jinie's backend needs to manipulate generated
source code in-memory before it is written to disk by the FileHandler —
e.g. inserting a CodeT5-small generated component, reformatting output,
or validating syntax before the Compiler assembles the project. Any
concrete editor (Python-focused, TSX-focused, etc.) must implement this.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple


class ICodeEditor(ABC):
    """Contract for in-memory code manipulation used by Jinie's backend."""

    # ---------------------------------------------------------------
    # Content loading / access
    # ---------------------------------------------------------------

    @abstractmethod
    def load(self, content: str) -> None:
        """Load `content` into the editor's active buffer."""
        raise NotImplementedError

    @abstractmethod
    def get_content(self) -> str:
        """Return the current buffer content."""
        raise NotImplementedError

    @abstractmethod
    def set_content(self, content: str) -> None:
        """Replace the entire buffer content with `content`."""
        raise NotImplementedError

    # ---------------------------------------------------------------
    # Editing operations
    # ---------------------------------------------------------------

    @abstractmethod
    def insert_at_line(self, line_number: int, snippet: str) -> bool:
        """Insert `snippet` before the given 1-indexed `line_number`."""
        raise NotImplementedError

    @abstractmethod
    def replace_block(self, start_line: int, end_line: int, new_code: str) -> bool:
        """Replace the inclusive 1-indexed line range with `new_code`."""
        raise NotImplementedError

    @abstractmethod
    def delete_block(self, start_line: int, end_line: int) -> bool:
        """Delete the inclusive 1-indexed line range from the buffer."""
        raise NotImplementedError

    @abstractmethod
    def insert_component(self, component_name: str, component_code: str) -> bool:
        """
        Insert a named, generated component (e.g. a React Native TSX
        component from Module 05) into the buffer at an appropriate
        location, avoiding duplicate insertions of the same component.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------
    # Formatting / validation
    # ---------------------------------------------------------------

    @abstractmethod
    def format_code(self, language: str) -> str:
        """Return a formatted version of the current buffer for `language`."""
        raise NotImplementedError

    @abstractmethod
    def validate_syntax(self, language: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the current buffer's syntax for `language`.
        Returns (is_valid, error_message). error_message is None when valid.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------
    # Persistence hook (delegates actual disk I/O to IFileHandler)
    # ---------------------------------------------------------------

    @abstractmethod
    def get_diff_summary(self, original_content: str) -> str:
        """Return a short human-readable summary of changes vs `original_content`."""
        raise NotImplementedError