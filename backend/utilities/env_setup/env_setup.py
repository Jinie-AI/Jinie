"""
backend/utilities/env_setup/env_setup.py
==========================================
Concrete implementation of IEnvSetupManager for the Jinie_main project.

Sprint 1  :  verify_dependencies, create_directories,
             set_environment_variables, install_requirements
Sprint 2  :  per-package version pinning/upgrade, npm dependency
             installation alongside pip

Where this sits in the Jinie pipeline
--------------------------------------
  [main.py boot / Compiler preparing a workspace]
                    │
                    ▼
          EnvSetupManager.verify_dependencies()
                    │  DependencyReport
                    ▼
          EnvSetupManager.create_directories(base_path, [...])
                    │  DirectoryResult
                    ▼   FileHandler.write(...) drops generated files in
          EnvSetupManager.set_environment_variables({...})
"""

import os
import re
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from backend.utilities.env_setup.env_setup_contract import (
    IEnvSetupManager,
    DependencyCheck,
    DependencyReport,
    DirectoryResult,
    EnvVarResult,
    InstallResult,
    EnvSetupError,
)


# ── private helpers ───────────────────────────────────────────────────────────

def _make_trace_id() -> str:
    """Every operation gets a unique ID registered in Traceability Matrix."""
    import uuid
    return f"ES-{uuid.uuid4()}"


def _resolve(path: str) -> str:
    """Return absolute, normalised path string."""
    return str(Path(path).resolve())


def _validate(path: str) -> None:
    """Raise INVALID_PATH if path is empty or blank."""
    if not path or not path.strip():
        raise EnvSetupError(
            "INVALID_PATH",
            "path must be a non-empty string.",
            path,
        )


def _log_entry(op: str, target: str, tid: str, extra: dict | None = None) -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": op,
        "target":    target,
        "trace_id":  tid,
    }
    if extra:
        entry.update(extra)
    return entry


def _run_version_command(command: list) -> str:
    """
    Run a --version style command and return its raw stdout+stderr, or
    "" if the tool isn't installed / the command failed / timed out.
    Never raises — a missing tool is a normal outcome here.
    """
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return ((proc.stdout or "") + (proc.stderr or "")).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""


_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def _parse_version(raw_output: str):
    """Pull the first x.y.z triple out of a command's output, or None."""
    match = _VERSION_RE.search(raw_output)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _format_version(version: tuple) -> str:
    return ".".join(str(part) for part in version)


_ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Default tools required for Jinie_main's own backend + the React
# Native (Expo) apps it generates. See main README prerequisites.
_DEFAULT_TOOLS: dict = {
    "python": {
        "command":      ["python3", "--version"],
        "min_version":  (3, 10, 0),
        "install_hint": "Install Python 3.10+ from https://python.org",
    },
    "node": {
        "command":      ["node", "--version"],
        "min_version":  (18, 0, 0),
        "install_hint": "Install Node.js 18+ from https://nodejs.org",
    },
    "npm": {
        "command":      ["npm", "--version"],
        "min_version":  (8, 0, 0),
        "install_hint": "npm ships with Node.js — reinstall Node.js if missing",
    },
    "expo": {
        # --no-install stops npx from silently fetching Expo CLI over
        # the network just to answer a version check
        "command":      ["npx", "--no-install", "expo", "--version"],
        "min_version":  None,
        "install_hint": "Run: npm install --global expo-cli",
    },
}


# ── implementation ────────────────────────────────────────────────────────────

class EnvSetupManager(IEnvSetupManager):
    """
    Verifies local tooling, prepares workspace directories, applies
    environment variables, and installs Python requirements for the
    Jinie_main pipeline.

    Quick usage
    -----------
        es = EnvSetupManager()

        report = es.verify_dependencies()
        if not report.all_satisfied:
            ...  # surface report.checks[i].install_hint to the user

        es.create_directories("/workspace/Jinie_main", ["backend/generated"])
        es.set_environment_variables({"FIREBASE_PROJECT_ID": "jinie-main-prod"})
    """

    def __init__(self) -> None:
        # Logger (Module 08) reads this via get_log()
        self._log: list[dict] = []

    # ── verify_dependencies ──────────────────────────────────────────────────

    def verify_dependencies(self, required_tools: dict = None) -> DependencyReport:
        """
        Verify that all required local tooling is present and meets its
        minimum version. See _DEFAULT_TOOLS for the Sprint 1 tool set.

        In Jinie this is called for:
          • main.py's boot-time gate for Jinie_main's backend service
          • Module 08's preflight sweep before deployment
        """
        tools = required_tools if required_tools is not None else _DEFAULT_TOOLS
        tid = _make_trace_id()
        checks: list = []

        for name, spec in tools.items():
            raw_output = _run_version_command(spec["command"])
            found_version = _parse_version(raw_output)
            min_version = spec.get("min_version")

            if found_version is None:
                satisfied = False
                found_str = ""
            elif min_version is None:
                satisfied = True
                found_str = _format_version(found_version)
            else:
                satisfied = found_version >= min_version
                found_str = _format_version(found_version)

            required_str = (f">={_format_version(min_version)}"
                             if min_version else "any")

            checks.append(DependencyCheck(
                name              = name,
                command           = " ".join(spec["command"]),
                found_version     = found_str,
                required_version  = required_str,
                satisfied         = satisfied,
                install_hint      = "" if satisfied else spec["install_hint"],
            ))

        report = DependencyReport(
            all_satisfied = all(c.satisfied for c in checks),
            checks        = checks,
            trace_id      = tid,
        )

        self._log.append(_log_entry("VERIFY", ",".join(tools.keys()), tid, {
            "all_satisfied": report.all_satisfied,
        }))
        return report

    # ── create_directories ───────────────────────────────────────────────────

    def create_directories(self, base_path: str, directories: list) -> DirectoryResult:
        """
        Create the given relative sub-directories under base_path.
        Existing directories are left untouched and reported in .skipped.

        In Jinie this is called for:
          • Compiler preparing a workspace before FileHandler writes
            generated files into it
          • Logger ensuring its log directory exists before first write
        """
        _validate(base_path)
        absp = _resolve(base_path)
        tid = _make_trace_id()

        created: list = []
        skipped: list = []

        try:
            Path(absp).mkdir(parents=True, exist_ok=True)

            for rel_dir in directories:
                dir_path = Path(absp) / rel_dir
                if dir_path.exists():
                    skipped.append(str(dir_path))
                else:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created.append(str(dir_path))
        except PermissionError:
            raise EnvSetupError("PERMISSION_ERROR",
                                 "Write permission denied.", absp)

        result = DirectoryResult(
            base_path = absp,
            created   = created,
            skipped   = skipped,
            trace_id  = tid,
        )

        self._log.append(_log_entry("CREATE_DIRS", absp, tid, {
            "created_count": len(created),
            "skipped_count": len(skipped),
        }))
        return result

    # ── set_environment_variables ────────────────────────────────────────────

    def set_environment_variables(self, variables: dict,
                                   persist_path: str = None) -> EnvVarResult:
        """
        Apply variables to os.environ for the current process, and
        optionally persist them into an env file for future runs.

        In Jinie this is called for:
          • Applying Firebase / API credentials before deployment
          • Applying the user's design tokens as EXPO_PUBLIC_* variables
        """
        tid = _make_trace_id()
        applied: list = []
        skipped: list = []

        for key, value in variables.items():
            if not _ENV_KEY_RE.match(key or ""):
                skipped.append(key)
                continue
            os.environ[key] = str(value)
            applied.append(key)

        persisted_path = ""
        if persist_path:
            absp = _resolve(persist_path)
            existing: dict = {}
            if os.path.exists(absp):
                for line in Path(absp).read_text(encoding="utf-8").splitlines():
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    if "=" in line:
                        k, _, v = line.partition("=")
                        existing[k.strip()] = v.strip()

            for key in applied:
                existing[key] = os.environ[key]

            try:
                Path(absp).parent.mkdir(parents=True, exist_ok=True)
                body = "".join(f"{k}={v}\n" for k, v in existing.items())
                Path(absp).write_text(body, encoding="utf-8")
            except PermissionError:
                raise EnvSetupError("PERMISSION_ERROR",
                                     "Write permission denied.", absp)
            persisted_path = absp

        result = EnvVarResult(
            variables_set     = applied,
            variables_skipped = skipped,
            persisted_path    = persisted_path,
            trace_id          = tid,
        )

        self._log.append(_log_entry("SET_ENV", persisted_path or "<process>", tid, {
            "applied": applied,
            "skipped": skipped,
        }))
        return result

    # ── install_requirements ─────────────────────────────────────────────────

    def install_requirements(self, requirements_file: str) -> InstallResult:
        """
        Install Python packages listed in a requirements.txt via pip.

        In Jinie this is called for:
          • Installing Jinie_main's own backend dependencies before boot
        """
        _validate(requirements_file)
        absp = _resolve(requirements_file)
        tid = _make_trace_id()

        if not os.path.isfile(absp):
            raise EnvSetupError("REQUIREMENTS_FILE_NOT_FOUND",
                                 "requirements file does not exist.", absp)

        lines = Path(absp).read_text(encoding="utf-8").splitlines()
        actionable = [ln for ln in lines
                      if ln.strip() and not ln.strip().startswith("#")]

        if not actionable:
            # nothing to install — skip the subprocess call entirely
            result = InstallResult(
                success            = True,
                requirements_file  = absp,
                output             = "Nothing to install (requirements file is empty).",
                trace_id           = tid,
            )
            self._log.append(_log_entry("INSTALL", absp, tid, {"success": True}))
            return result

        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", absp],
                capture_output=True,
                text=True,
                timeout=600,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
            raise EnvSetupError("INSTALL_FAILED", str(exc), absp)

        output = ((proc.stdout or "") + (proc.stderr or "")).strip()
        success = (proc.returncode == 0)

        if not success:
            raise EnvSetupError("INSTALL_FAILED",
                                 f"pip exited with code {proc.returncode}: "
                                 f"{output[-500:]}",
                                 absp)

        result = InstallResult(
            success            = success,
            requirements_file  = absp,
            output             = output[-4000:],  # tail-truncate long pip logs
            trace_id           = tid,
        )

        self._log.append(_log_entry("INSTALL", absp, tid, {
            "success": success,
        }))
        return result

    # ── log ───────────────────────────────────────────────────────────────────

    def get_log(self) -> list[dict]:
        """
        Return snapshot of the internal log.
        Module 08 (Logger) reads this for audit and preflight checks.
        """
        return list(self._log)
