"""Safe, sandboxed file writing utilities for generated project output."""

from __future__ import annotations

from pathlib import Path

from .exceptions import ValidationError


def safe_relative_path(base: Path, *parts: str) -> Path:
    """Join path parts under `base`, rejecting any attempt to escape it."""
    candidate = base.joinpath(*parts).resolve()
    base_resolved = base.resolve()
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise ValidationError(f"Path {candidate} escapes output directory {base_resolved}.")
    return candidate


class FileWriter:
    """Writes generated files into an output directory, guarding against
    path traversal outside of that directory.
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def write(self, relative_path: str, content: str) -> None:
        path = safe_relative_path(self.output_dir, relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def safe_path(self, *parts: str) -> Path:
        return safe_relative_path(self.output_dir, *parts)
