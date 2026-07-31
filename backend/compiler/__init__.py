"""
Compiler Module

Public interface for the React Native Compiler Engine.

Exports:
    - CompilerEngine
    - CompilerBuilder
    - AppConfig
    - NavRoute
    - StateManager
    - NavigationType
    - StateManagerType
    - CompilerError
    - ValidationError
    - CompilationError
"""

from .compiler import (
    AppConfig,
    CompilerBuilder,
    CompilerEngine,
    CompilationError,
    CompilerError,
    NavRoute,
    NavigationType,
    StateManager,
    StateManagerType,
    ValidationError,
)

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
]

__version__ = "1.0.0"
__author__ = "Jinie"