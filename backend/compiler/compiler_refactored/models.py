"""Dataclasses / models used across the compiler package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .constants import _VALID_NAME_RE
from .enums import StateManagerType
from .exceptions import ValidationError
from .helpers import slugify


@dataclass
class NavRoute:
    """Represents a single navigation route."""

    name: str
    component: str  # screen filename, e.g. "HomeScreen.tsx"
    title: Optional[str] = None
    icon: Optional[str] = None
    initial_route: bool = False
    screen_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not _VALID_NAME_RE.match(self.name):
            raise ValidationError(
                f"Route name {self.name!r} must start with a letter and contain "
                "only letters, digits, or underscores."
            )
        if not self.component:
            raise ValidationError(f"Route {self.name!r} is missing a component filename.")
        if not self.component.endswith((".tsx", ".ts")):
            raise ValidationError(
                f"Route {self.name!r} component {self.component!r} must end in .tsx or .ts"
            )


@dataclass
class StateManager:
    """Represents a state management solution."""

    name: str
    type: StateManagerType
    stores: List[str] = field(default_factory=list)
    version: str = "latest"

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            try:
                self.type = StateManagerType(self.type)
            except ValueError as exc:
                valid = ", ".join(t.value for t in StateManagerType)
                raise ValidationError(
                    f"Unknown state manager type {self.type!r}. Valid options: {valid}"
                ) from exc


@dataclass
class AppConfig:
    """Main application configuration."""

    name: str
    display_name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    slug: str = ""
    icon: str = "./assets/icon.png"
    splash: Dict[str, str] = field(
        default_factory=lambda: {
            "image": "./assets/splash.png",
            "resizeMode": "contain",
            "backgroundColor": "#ffffff",
        }
    )
    orientation: str = "portrait"
    primary_color: str = "#007AFF"
    background_color: str = "#ffffff"
    bundle_id_prefix: str = "com.jinie"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValidationError("AppConfig.name is required.")
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.slug)
        if not self.slug:
            raise ValidationError(f"Could not derive a valid slug from name {self.name!r}.")

    @property
    def bundle_identifier(self) -> str:
        package_segment = self.slug.replace("-", "")
        return f"{self.bundle_id_prefix}.{package_segment}"
