"""Creates the base directory structure of the generated project."""

from __future__ import annotations

from pathlib import Path

from ..file_writer import safe_relative_path


def create_directory_structure(output_dir: Path) -> None:
    """Create the standard Expo/React Native project directory layout."""
    directories = [
        "src",
        "src/navigation",
        "src/screens",
        "src/components",
        "src/state",
        "src/state/actions",
        "src/state/reducers",
        "src/state/selectors",
        "src/services",
        "src/utils",
        "src/constants",
        "src/types",
        "src/hooks",
        "assets",
        "assets/images",
        "assets/fonts",
        "assets/icons",
    ]
    for directory in directories:
        safe_relative_path(output_dir, directory).mkdir(parents=True, exist_ok=True)
