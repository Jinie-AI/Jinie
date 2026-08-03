"""Compiler Engine orchestrator.

Owns the compiler's mutable state (routes, state managers, components,
static data, navigation structure) and the public registration API, and
drives the `compile()` pipeline by delegating each generation step to the
appropriate generator in `compiler.generators`.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .constants import _VALID_NAME_RE
from .enums import NavigationType
from .exceptions import CompilationError, CompilerError, ValidationError
from .file_writer import FileWriter
from .generators.app_entry import AppEntryGenerator
from .generators.components import ComponentsGenerator
from .generators.config_files import ConfigFilesGenerator
from .generators.directory_scaffold import create_directory_structure
from .generators.env_files import EnvFilesGenerator
from .generators.navigation import NavigationGenerator
from .generators.state_management import StateManagementGenerator
from .generators.static_data import StaticDataGenerator
from .generators.utilities import UtilitiesGenerator
from .models import AppConfig, NavRoute, StateManager

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Compiler Engine
# --------------------------------------------------------------------------- #
class CompilerEngine:
    """Orchestrates the compilation of React Native components into a
    complete, executable Expo project.
    """

    def __init__(self, output_dir: str, config: Optional[AppConfig] = None) -> None:
        self.output_dir = Path(output_dir)
        self.config = config or AppConfig(
            name="JinieApp", display_name="Jinie Application", slug="jinie-app"
        )
        self.routes: List[NavRoute] = []
        self.state_managers: List[StateManager] = []
        self.components: Dict[str, Dict[str, Any]] = {}
        self.static_data: Dict[str, Any] = {}
        self.navigation_structure: Dict[str, Any] = {"type": NavigationType.STACK.value}

    # -- registration API ---------------------------------------------------
    def add_route(self, route: NavRoute) -> None:
        if any(r.name == route.name for r in self.routes):
            raise ValidationError(f"Duplicate route name: {route.name!r}")
        self.routes.append(route)

    def add_state_manager(self, manager: StateManager) -> None:
        self.state_managers.append(manager)

    def add_component(self, name: str, content: Dict[str, Any]) -> None:
        if not _VALID_NAME_RE.match(name):
            raise ValidationError(f"Invalid component name: {name!r}")
        self.components[name] = content

    def add_static_data(self, key: str, data: Any) -> None:
        try:
            json.dumps(data)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"Static data for key {key!r} is not JSON-serializable.") from exc
        self.static_data[key] = data

    def set_navigation_structure(self, structure: Dict[str, Any]) -> None:
        nav_type = structure.get("type", NavigationType.STACK.value)
        try:
            NavigationType(nav_type)
        except ValueError as exc:
            valid = ", ".join(t.value for t in NavigationType)
            raise ValidationError(
                f"Unknown navigation type {nav_type!r}. Valid options: {valid}"
            ) from exc
        self.navigation_structure = structure

    # -- compilation ----------------------------------------------------
    def compile(self) -> bool:
        """Execute the full compilation process.

        Returns:
            True if compilation succeeded.

        Raises:
            CompilationError: if any generation step fails. The partially
                generated output directory is left in place for inspection.
        """
        if not self.routes:
            raise ValidationError("Cannot compile an app with zero routes.")

        writer = FileWriter(self.output_dir)

        config_files_gen = ConfigFilesGenerator(self.config, self.state_managers, writer)
        app_entry_gen = AppEntryGenerator(self.state_managers, writer)
        navigation_gen = NavigationGenerator(
            self.routes, self.components, self.navigation_structure, self.config, writer
        )
        components_gen = ComponentsGenerator(self.components, writer)
        state_management_gen = StateManagementGenerator(self.state_managers, writer)
        static_data_gen = StaticDataGenerator(self.static_data, writer)
        utilities_gen = UtilitiesGenerator(writer)
        env_files_gen = EnvFilesGenerator(writer)

        steps = [
            ("directory structure", lambda: create_directory_structure(self.output_dir)),
            ("app.json", config_files_gen.generate_app_json),
            ("package.json", config_files_gen.generate_package_json),
            ("tsconfig.json", config_files_gen.generate_tsconfig),
            ("babel.config.js", config_files_gen.generate_babel_config),
            ("App.tsx", app_entry_gen.generate_app_tsx),
            ("navigation", navigation_gen.generate_navigation_structure),
            ("components", components_gen.generate_components),
            ("state management", state_management_gen.generate_state_management),
            ("static data", static_data_gen.generate_static_data),
            ("utilities", utilities_gen.generate_utilities),
            ("env files", env_files_gen.generate_env_files),
            ("gitignore", config_files_gen.generate_gitignore),
        ]

        for step_name, step_fn in steps:
            try:
                step_fn()
            except CompilerError:
                raise
            except Exception as exc:  # noqa: BLE001 - surfaced as CompilationError
                raise CompilationError(f"Failed while generating {step_name}: {exc}") from exc

        logger.info("Compilation successful. Project generated at: %s", self.output_dir)
        return True

    # -- reporting ------------------------------------------------------
    def generate_report(self) -> Dict[str, Any]:
        """Generate a JSON-serializable compilation report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "appName": self.config.name,
            "version": self.config.version,
            "outputDirectory": str(self.output_dir),
            "routes": len(self.routes),
            "components": len(self.components),
            "stateManagers": [
                {**asdict(m), "type": m.type.value} for m in self.state_managers
            ],
            "navigationStructure": self.navigation_structure,
            "status": "completed",
        }
