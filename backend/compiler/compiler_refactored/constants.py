"""Shared regex constants used across the compiler package."""

from __future__ import annotations

import re

_VALID_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_SLUG_SANITIZE_RE = re.compile(r"[^a-z0-9-]+")
_NAME_SPLIT_RE = re.compile(r"[^0-9A-Za-z]+")
