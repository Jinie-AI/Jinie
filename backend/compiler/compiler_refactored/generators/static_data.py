"""Generates static constants files: colors, spacing, typography, and any
user-registered static data.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from ..file_writer import FileWriter


class StaticDataGenerator:
    """Generates constants and static-data files."""

    def __init__(self, static_data: Dict[str, Any], writer: FileWriter) -> None:
        self._static_data = static_data
        self._writer = writer

    # -- static data / constants ---------------------------------------------
    def generate_static_data(self) -> None:
        self._writer.write(
            "src/constants/colors.ts",
            """export const Colors = {
  primary: '#007AFF',
  secondary: '#5AC8FA',
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  white: '#FFFFFF',
  black: '#000000',
  gray: '#8E8E93',
  lightGray: '#F2F2F7',
} as const;
""",
        )
        self._writer.write(
            "src/constants/spacing.ts",
            """export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;
""",
        )
        self._writer.write(
            "src/constants/typography.ts",
            """export const Typography = {
  h1: { fontSize: 32, fontWeight: '700', lineHeight: 38 },
  h2: { fontSize: 24, fontWeight: '600', lineHeight: 30 },
  body: { fontSize: 16, fontWeight: '400', lineHeight: 24 },
  caption: { fontSize: 12, fontWeight: '400', lineHeight: 16 },
} as const;
""",
        )
        if self._static_data:
            data_content = "export const DATA = " + json.dumps(self._static_data, indent=2) + " as const;\n"
            self._writer.write("src/constants/data.ts", data_content)
