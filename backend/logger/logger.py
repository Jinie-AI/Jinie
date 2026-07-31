"""
logger.py

Logger Submodule.
Tracks system events and performs pre-deployment boot checks.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

_python_logger = logging.getLogger("jinie.srs")
if not _python_logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _python_logger.addHandler(_handler)
    _python_logger.setLevel(logging.DEBUG)
    _python_logger.propagate = False


class Logger:
    """
    Trace-indexed, structured logger for the SRS pipeline. Every log
    line includes an ISO-8601 UTC timestamp, the emitting module name,
    the log level, and the message — parseable by the frontend's
    LiveLogStream as it streams in.
    """

    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id

    def log_event(
        self,
        module_name: str,
        message: str,
        level: str = "INFO",
        trace_id: Optional[str] = None,
    ) -> None:
        """Logs a pipeline message with timestamps."""
        resolved_level = level.upper() if level and level.upper() in _VALID_LEVELS else "INFO"
        resolved_trace_id = trace_id or self.trace_id or "no-trace-id"
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        formatted = (
            f"{timestamp} | trace_id={resolved_trace_id} | module={module_name} | "
            f"level={resolved_level} | {message}"
        )

        log_fn = {
            "DEBUG": _python_logger.debug,
            "INFO": _python_logger.info,
            "WARNING": _python_logger.warning,
            "ERROR": _python_logger.error,
            "CRITICAL": _python_logger.critical,
        }[resolved_level]

        log_fn(formatted)

    def run_preflight_checks(self, project_path: str) -> bool:
        """Runs the boot-check and authentication verification tests before deployment."""
        self.log_event("logger.py", f"Starting preflight checks for project_path='{project_path}'", level="INFO")

        all_passed = True
        path = Path(project_path)

        if not path.exists():
            self.log_event("logger.py", f"Preflight FAILED: project_path does not exist: {project_path}", level="ERROR")
            all_passed = False
        elif not path.is_dir():
            self.log_event("logger.py", f"Preflight FAILED: project_path is not a directory: {project_path}", level="ERROR")
            all_passed = False
        else:
            self.log_event("logger.py", "Preflight OK: project_path exists and is a directory", level="INFO")

        if path.exists() and path.is_dir():
            if not os.access(path, os.R_OK):
                self.log_event("logger.py", f"Preflight FAILED: project_path is not readable: {project_path}", level="ERROR")
                all_passed = False
            elif not os.access(path, os.W_OK):
                self.log_event("logger.py", f"Preflight FAILED: project_path is not writable: {project_path}", level="ERROR")
                all_passed = False
            else:
                self.log_event("logger.py", "Preflight OK: project_path is readable and writable", level="INFO")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            self.log_event(
                "logger.py",
                "Preflight FAILED: GROQ_API_KEY is not set. Get a free key at https://console.groq.com",
                level="ERROR",
            )
            all_passed = False
        elif not api_key.startswith("gsk_"):
            self.log_event(
                "logger.py",
                "Preflight WARNING: GROQ_API_KEY is set but does not match the expected 'gsk_' prefix format",
                level="WARNING",
            )
        else:
            self.log_event("logger.py", "Preflight OK: GROQ_API_KEY is present and correctly formatted", level="INFO")

        if all_passed:
            self.log_event("logger.py", "All preflight checks PASSED", level="INFO")
        else:
            self.log_event("logger.py", "One or more preflight checks FAILED — see errors above", level="CRITICAL")

        return all_passed