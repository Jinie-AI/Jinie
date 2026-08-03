"""Fluent builder for configuring and running a CompilerEngine."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .engine import CompilerEngine
from .models import AppConfig, NavRoute, StateManager


class CompilerBuilder:
    """Fluent builder for configuring and running a CompilerEngine."""

    def __init__(self, output_dir: str) -> None:
        self.compiler = CompilerEngine(output_dir)

    def set_config(self, config: AppConfig) -> "CompilerBuilder":
        self.compiler.config = config
        return self

    def add_route(
        self, name: str, component: str, title: Optional[str] = None, initial: bool = False
    ) -> "CompilerBuilder":
        self.compiler.add_route(
            NavRoute(name=name, component=component, title=title or name, initial_route=initial)
        )
        return self

    def add_state_manager(
        self, name: str, manager_type: str, version: str = "latest"
    ) -> "CompilerBuilder":
        self.compiler.add_state_manager(StateManager(name=name, type=manager_type, version=version))
        return self

    def add_component(self, name: str, content: Dict[str, Any]) -> "CompilerBuilder":
        self.compiler.add_component(name, content)
        return self

    def add_static_data(self, key: str, data: Any) -> "CompilerBuilder":
        self.compiler.add_static_data(key, data)
        return self

    def set_navigation_structure(self, structure: Dict[str, Any]) -> "CompilerBuilder":
        self.compiler.set_navigation_structure(structure)
        return self

    def build(self) -> CompilerEngine:
        return self.compiler

    def compile(self) -> bool:
        return self.compiler.compile()
