"""Generates .env environment files for development, production, and the
example template.
"""

from __future__ import annotations

from ..file_writer import FileWriter


class EnvFilesGenerator:
    """Generates the project's .env* files."""

    def __init__(self, writer: FileWriter) -> None:
        self._writer = writer

    # -- environment files ----------------------------------------------
    def generate_env_files(self) -> None:
        self._writer.write(
            ".env.development",
            "# Development environment\n"
            "EXPO_PUBLIC_API_URL=http://localhost:3000\n"
            "EXPO_PUBLIC_APP_ENV=development\n",
        )
        self._writer.write(
            ".env.production",
            "# Production environment - fill in real values before deploying\n"
            "EXPO_PUBLIC_API_URL=https://api.production.example.com\n"
            "EXPO_PUBLIC_APP_ENV=production\n",
        )
        self._writer.write(
            ".env.example",
            "# Copy this file to .env.development / .env.production and fill in values\n"
            "EXPO_PUBLIC_API_URL=http://localhost:3000\n"
            "EXPO_PUBLIC_APP_ENV=development\n",
        )
