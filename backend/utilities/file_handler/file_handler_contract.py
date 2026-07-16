"""
file_handler_contract.py

Contract (interface) for Module 01 — Utilities: File Handler.

Any concrete file handler used across Jinie's backend (Engine Coordinator,
Compiler, Deployment, etc.) must implement this interface. Keeping this as
an abstract contract lets other modules depend on IFileHandler instead of
a concrete class, so the implementation (local disk, in-memory, cloud
storage, etc.) can be swapped without touching callers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Union


class IFileHandler(ABC):
    """Contract for all filesystem operations used by Jinie's backend."""

    # ---------------------------------------------------------------
    # File-level operations
    # ---------------------------------------------------------------

    @abstractmethod
    def read_file(self, path: str) -> str:
        """Return the full text content of the file at `path`."""
        raise NotImplementedError

    @abstractmethod
    def write_file(self, path: str, content: str, overwrite: bool = True) -> bool:
        """
        Write `content` to `path`. Creates parent directories if needed.
        Returns True on success, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def append_file(self, path: str, content: str) -> bool:
        """Append `content` to the end of the file at `path`."""
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """Delete the file at `path`. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file from `source` to `destination`."""
        raise NotImplementedError

    @abstractmethod
    def move_file(self, source: str, destination: str) -> bool:
        """Move/rename a file from `source` to `destination`."""
        raise NotImplementedError

    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Return True if a file exists at `path`."""
        raise NotImplementedError

    @abstractmethod
    def get_file_size(self, path: str) -> int:
        """Return file size in bytes."""
        raise NotImplementedError

    # ---------------------------------------------------------------
    # Directory-level operations
    # ---------------------------------------------------------------

    @abstractmethod
    def create_directory(self, path: str) -> bool:
        """Create a directory (and any missing parents) at `path`."""
        raise NotImplementedError

    @abstractmethod
    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        """Delete a directory at `path`."""
        raise NotImplementedError

    @abstractmethod
    def directory_exists(self, path: str) -> bool:
        """Return True if a directory exists at `path`."""
        raise NotImplementedError

    @abstractmethod
    def list_directory(self, path: str) -> List[str]:
        """Return a list of entry names (files + folders) inside `path`."""
        raise NotImplementedError

    # ---------------------------------------------------------------
    # Project scaffolding (used by Module 06: Compiler)
    # ---------------------------------------------------------------

    @abstractmethod
    def create_project_scaffold(
        self, root_path: str, structure: Dict[str, Union[dict, str, None]]
    ) -> bool:
        """
        Create a full folder/file tree at `root_path` from a nested dict.
        Keys ending without a recognizable file extension are treated as
        directories; string/None leaf values are treated as files whose
        value (if any) is written as initial content.
        """
        raise NotImplementedError