"""Custom exceptions raised by the compiler package."""

from __future__ import annotations


class CompilerError(Exception):
    """Base exception for all compiler-related failures."""


class ValidationError(CompilerError):
    """Raised when input configuration is invalid."""


class CompilationError(CompilerError):
    """Raised when the compilation process fails."""
