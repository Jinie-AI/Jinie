"""
file_handler.py

Concrete implementation of IFileHandler using the local filesystem
(pathlib + shutil). This is the default handler used by Jinie's backend
for all local, on-disk operations: writing generated React Native
component files, scaffolding Expo projects, managing SRS documents, etc.
"""

import shutil
from pathlib import Path
from typing import List, Dict, Union

from file_handler_contract import IFileHandler


class FileHandler(IFileHandler):
    """Local-disk implementation of the file handler contract."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else (self.base_path / p)

    # ---------------------------------------------------------------
    # File-level operations
    # ---------------------------------------------------------------

    def read_file(self, path: str) -> str:
        target = self._resolve(path)
        try:
            return target.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {target}")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Could not decode file as UTF-8: {target}") from exc

    def write_file(self, path: str, content: str, overwrite: bool = True) -> bool:
        target = self._resolve(path)
        try:
            if target.exists() and not overwrite:
                return False
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return True
        except OSError:
            return False

    def append_file(self, path: str, content: str) -> bool:
        target = self._resolve(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("a", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError:
            return False

    def delete_file(self, path: str) -> bool:
        target = self._resolve(path)
        try:
            target.unlink(missing_ok=True)
            return True
        except OSError:
            return False

    def copy_file(self, source: str, destination: str) -> bool:
        src, dest = self._resolve(source), self._resolve(destination)
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            return True
        except OSError:
            return False

    def move_file(self, source: str, destination: str) -> bool:
        src, dest = self._resolve(source), self._resolve(destination)
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            return True
        except OSError:
            return False

    def file_exists(self, path: str) -> bool:
        return self._resolve(path).is_file()

    def get_file_size(self, path: str) -> int:
        target = self._resolve(path)
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {target}")
        return target.stat().st_size

    # ---------------------------------------------------------------
    # Directory-level operations
    # ---------------------------------------------------------------

    def create_directory(self, path: str) -> bool:
        target = self._resolve(path)
        try:
            target.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False

    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        target = self._resolve(path)
        try:
            if recursive:
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.rmdir()
            return True
        except OSError:
            return False

    def directory_exists(self, path: str) -> bool:
        return self._resolve(path).is_dir()

    def list_directory(self, path: str) -> List[str]:
        target = self._resolve(path)
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {target}")
        return sorted(entry.name for entry in target.iterdir())

    # ---------------------------------------------------------------
    # Project scaffolding
    # ---------------------------------------------------------------

    def create_project_scaffold(
        self, root_path: str, structure: Dict[str, Union[dict, str, None]]
    ) -> bool:
        root = self._resolve(root_path)
        try:
            self._build_tree(root, structure)
            return True
        except OSError:
            return False

    def _build_tree(self, current_path: Path, node: Dict[str, Union[dict, str, None]]) -> None:
        current_path.mkdir(parents=True, exist_ok=True)
        for name, value in node.items():
            entry_path = current_path / name
            if isinstance(value, dict):
                self._build_tree(entry_path, value)
            else:
                entry_path.parent.mkdir(parents=True, exist_ok=True)
                entry_path.write_text(value or "", encoding="utf-8")