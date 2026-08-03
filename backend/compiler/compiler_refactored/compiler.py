"""Compiler Engine Module (compiler.py)

Wires up page navigation, integrates state managers, injects static data, and
generates the entry points (App.tsx, package.json, app.json, navigation
routes) of a React Native (with Expo) project.

This module serves as the final compilation step that takes:
  - Generated components (from Module 5)
  - Functional requirements / sitemap (from Module 4)
and compiles them into a single coherent React Native application project.

This module is now a thin entry point: the actual implementation lives in
the sibling modules of the `compiler` package (models, helpers, engine,
builder, generators/...). Everything that used to be importable from
`compiler.compiler` remains importable from here for backward compatibility.
"""

from __future__ import annotations

import logging

from .builder import CompilerBuilder
from .engine import CompilerEngine
from .enums import NavigationType, StateManagerType
from .exceptions import CompilationError, CompilerError, ValidationError
from .helpers import slugify, to_pascal_case, to_screen_component_name
from .models import AppConfig, NavRoute, StateManager

logger = logging.getLogger(__name__)

__all__ = [
    "CompilerEngine",
    "CompilerBuilder",
    "AppConfig",
    "NavRoute",
    "StateManager",
    "NavigationType",
    "StateManagerType",
    "CompilerError",
    "ValidationError",
    "CompilationError",
    "slugify",
    "to_pascal_case",
    "to_screen_component_name",
]


# --------------------------------------------------------------------------- #
# Example usage / CLI entry point
# --------------------------------------------------------------------------- #
def _main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    output_path = "./generated_app"
    config = AppConfig(
        name="MyApp",
        display_name="My Application",
        slug="my-app",
        version="1.0.0",
        description="Auto-generated React Native app",
        author="Jinie",
    )

    try:
        builder = (
            CompilerBuilder(output_path)
            .set_config(config)
            .add_route("Home", "HomeScreen.tsx", "Home", initial=True)
            .add_route("Profile", "ProfileScreen.tsx", "Profile")
            .add_route("Settings", "SettingsScreen.tsx", "Settings")
            .add_state_manager("Redux Store", "redux", "^4.2.1")
            .add_component("Button", {"props": {"label": "string", "onPress": "() => void"}})
            .add_component("Card", {"props": {"title": "string", "content": "string"}})
            .add_static_data("apiUrl", "https://api.example.com")
            .set_navigation_structure({"type": "stack", "initialRoute": "Home"})
        )
        builder.compile()
    except CompilerError as exc:
        logger.error("Compilation failed: %s", exc)
        return 1

    logger.info("React Native app successfully generated!")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
