"""Enums shared across the compiler package."""

from __future__ import annotations

from enum import Enum


class NavigationType(str, Enum):
    """Supported navigation types in the app."""

    STACK = "stack"
    TAB = "tab"
    DRAWER = "drawer"
    BOTTOM_TAB = "bottom_tab"


class StateManagerType(str, Enum):
    """Supported state management solutions."""

    REDUX = "redux"
    ZUSTAND = "zustand"
    CONTEXT = "context"
    RECOIL = "recoil"
