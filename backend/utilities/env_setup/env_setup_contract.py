"""
================================================================
CONTRACT  :  EnvSetupManager
MODULE    :  backend/utilities/env_setup
VERSION   :  1.0.0   |   Sprint 1
================================================================

WHO USES THIS IN JINIE
-----------------------
EnvSetupManager is the only class in Jinie allowed to touch local
tooling, process environment variables, and package installation.

  main.py (backend service boot for Jinie_main)
              │
              ▼
      EnvSetupManager.verify_dependencies()
              │  DependencyReport
              ▼
      Logger (Module 08) blocks the UI from starting a build
      if DependencyReport.all_satisfied is False, and shows the
      install hints in ErrorAlerts (frontend Module 12)

  Module 06 (Compiler) — preparing the workspace for a new build
              │
              ▼
      EnvSetupManager.create_directories(base_path, [...])
              │  DirectoryResult
              ▼
      FileHandler.write(...)   ← Compiler drops CodeT5 output into
                                   the directories just created

  Module 09 (Deployment)
              │
              ▼
      EnvSetupManager.set_environment_variables({...})
              │  EnvVarResult
              ▼
      Firebase Helper reads os.environ for deploy credentials

REAL JINIE USAGE
-----------------
  es = EnvSetupManager()

  # Boot-time gate — main.py refuses to accept prompts if this fails
  report = es.verify_dependencies()
  if not report.all_satisfied:
      for check in report.checks:
          if not check.satisfied:
              logger.warn(f"{check.name}: {check.install_hint}")

  # Workspace prep for Jinie_main's own backend
  es.create_directories("/workspace/Jinie_main", [
      "backend/generated",
      "backend/logs",
  ])

  # Deploy-time credentials, both live in-process and persisted
  es.set_environment_variables(
      {"FIREBASE_PROJECT_ID": "jinie-main-prod"},
      persist_path="/workspace/Jinie_main/.env",
  )

  # Installing/pinning backend requirements before boot
  es.install_requirements("/workspace/Jinie_main/backend/requirements.txt")

WHAT EnvSetupManager GUARANTEES
---------------------------------
verify_dependencies(required_tools=None)
    → DependencyReport
        .all_satisfied   bool   True only if every check passed
        .checks          list[DependencyCheck]
        .trace_id        str    "ES-<uuid4>"

    DependencyCheck
        .name              str   e.g. "node"
        .command            str   the shell command that was run
        .found_version      str   e.g. "22.22.2"  ("" if not found)
        .required_version   str   e.g. ">=18.0.0"
        .satisfied          bool
        .install_hint       str   shown to the user when not satisfied

create_directories(base_path, directories)
    → DirectoryResult
        .base_path        str   absolute resolved base path
        .created          list[str]   absolute paths actually created
        .skipped          list[str]   absolute paths that already existed
        .trace_id         str   "ES-<uuid4>"

set_environment_variables(variables, persist_path=None)
    → EnvVarResult
        .variables_set          list[str]   keys applied to os.environ
        .variables_skipped      list[str]   keys rejected as unsafe
        .persisted_path         str         "" if persist_path not given
        .trace_id               str         "ES-<uuid4>"

install_requirements(requirements_file)
    → InstallResult
        .success            bool
        .requirements_file  str
        .output              str   raw pip stdout+stderr, tail-truncated
        .trace_id            str   "ES-<uuid4>"

get_log() → list[dict]   snapshot of every call (Logger reads this)

DEPENDENCY CHECKS (Sprint 1 default set — see main README prerequisites)
--------------------------------------------------------------------------
  node    node --version               required >= 18.0.0
  npm     npm --version                required >= 8.0.0
  expo    npx --no-install expo --version   required: any version found
          (checked with --no-install so a missing Expo CLI is reported
          instantly instead of triggering a silent npm-registry fetch)
  python  python3 --version            required >= 3.10.0

CONTRACT RULES
--------------
PRE  (caller must guarantee)
  1. base_path / requirements_file are always non-empty strings
  2. variables passed to set_environment_variables is dict[str, str]
  3. directories passed to create_directories are relative sub-paths
     under base_path, e.g. "backend/logs" — not absolute paths

POST (EnvSetupManager guarantees)
  1. verify_dependencies() never raises for a missing/old tool — a
     missing tool is a normal, reportable DependencyCheck, not an error
  2. create_directories() never deletes or overwrites an existing
     directory — creating an already-existing path is a no-op, reported
     in .skipped
  3. set_environment_variables() only ever sets keys matching
     ^[A-Za-z_][A-Za-z0-9_]*$ — anything else is rejected, not sanitised
  4. trace_id is always UUID4 prefixed "ES-"

ERROR CODES
-----------
  INVALID_PATH             base_path / requirements_file is empty or blank
  PERMISSION_ERROR          OS denied a filesystem write
  REQUIREMENTS_FILE_NOT_FOUND   install_requirements() path does not exist
  INSTALL_FAILED             pip exited non-zero

DOWNSTREAM (what the Compiler expects from DirectoryResult)
  Compiler writes generated component files under whichever path in
  DirectoryResult.created / .skipped matches its target output folder.

AGILE ROADMAP
  Sprint 1  verify_dependencies, create_directories,
            set_environment_variables, install_requirements
  Sprint 2  per-package version pinning/upgrade (not just requirements.txt
            install), npm dependency installation alongside pip
================================================================
"""

from dataclasses import dataclass


# ── data types ────────────────────────────────────────────────────────────────

@dataclass
class DependencyCheck:
    """One tool check inside a DependencyReport."""
    name:              str    # e.g. "node"
    command:           str    # the shell command that was run
    found_version:     str    # "" if the tool was not found at all
    required_version:  str    # e.g. ">=18.0.0"
    satisfied:          bool
    install_hint:       str


@dataclass
class DependencyReport:
    """Output of EnvSetupManager.verify_dependencies()."""
    all_satisfied: bool
    checks:         list       # list[DependencyCheck]
    trace_id:       str        # "ES-<uuid4>"


@dataclass
class DirectoryResult:
    """Output of EnvSetupManager.create_directories()."""
    base_path:  str
    created:     list   # list[str], absolute paths actually created
    skipped:     list   # list[str], absolute paths that already existed
    trace_id:    str    # "ES-<uuid4>"


@dataclass
class EnvVarResult:
    """Output of EnvSetupManager.set_environment_variables()."""
    variables_set:      list  # list[str] keys applied to os.environ
    variables_skipped:  list  # list[str] keys rejected as unsafe
    persisted_path:      str  # "" if persist_path was not given
    trace_id:            str  # "ES-<uuid4>"


@dataclass
class InstallResult:
    """Output of EnvSetupManager.install_requirements()."""
    success:            bool
    requirements_file:   str
    output:               str  # raw pip stdout+stderr, tail-truncated
    trace_id:             str  # "ES-<uuid4>"


# ── error type ────────────────────────────────────────────────────────────────

class EnvSetupError(Exception):
    """
    Raised by EnvSetupManager for every failure.

    Usage:
        except EnvSetupError as e:
            if e.code == "REQUIREMENTS_FILE_NOT_FOUND":
                ...
    """
    CODES = frozenset({
        "INVALID_PATH",
        "PERMISSION_ERROR",
        "REQUIREMENTS_FILE_NOT_FOUND",
        "INSTALL_FAILED",
    })

    def __init__(self, code: str, message: str, path: str = "") -> None:
        if code not in self.CODES:
            raise ValueError(f"Unknown EnvSetupError code: {code!r}")
        self.code = code
        self.path = path
        super().__init__(f"[EnvSetupManager/{code}] {message}  (path={path!r})")


# ── abstract interface ────────────────────────────────────────────────────────

class IEnvSetupManager:
    """
    Abstract contract.
    Every other module imports IEnvSetupManager, not the concrete class.
    This lets us swap implementations each sprint without breaking callers.
    """

    def verify_dependencies(self, required_tools: dict = None) -> DependencyReport:
        """
        Verify that all required local tooling (Node.js, npm, Expo CLI,
        Python) is present and meets its minimum version.

        Jinie uses this for:
          • main.py's boot-time gate, before any prompt is accepted
          • Module 08's preflight sweep, re-checked before deployment

        PRE  required_tools, if given, maps tool name -> spec dict
             matching the shape of _DEFAULT_TOOLS
        POST DependencyReport returned; a VERIFY entry added to the log
        ERR  never raises — a missing tool is a normal reportable result
        """
        raise NotImplementedError

    def create_directories(self, base_path: str, directories: list) -> DirectoryResult:
        """
        Create the given relative sub-directories under base_path.

        Jinie uses this for:
          • Module 06 Compiler preparing an output workspace before
            FileHandler writes any generated files into it
          • Logger ensuring its log directory exists before first write

        PRE   base_path non-empty; directories is list[str] of relative
              sub-paths (never absolute)
        POST  DirectoryResult returned; a CREATE_DIRS entry added to the log
        ERR   EnvSetupError(INVALID_PATH | PERMISSION_ERROR)
        """
        raise NotImplementedError

    def set_environment_variables(self, variables: dict,
                                   persist_path: str = None) -> EnvVarResult:
        """
        Apply variables to the current process's os.environ, and
        optionally persist them into an env file for future runs.

        Jinie uses this for:
          • Applying Firebase / API credentials before Module 09 deploy
          • Applying the user's Module 11 design tokens as build-time
            EXPO_PUBLIC_* variables for the current generation run

        PRE   variables is dict[str, str]; persist_path, if given, is a
              non-empty file path
        POST  os.environ updated in-process; env file merged (existing
              unrelated keys kept) if persist_path was given
        ERR   EnvSetupError(PERMISSION_ERROR)
        """
        raise NotImplementedError

    def install_requirements(self, requirements_file: str) -> InstallResult:
        """
        Install Python packages listed in a requirements.txt via pip.

        Jinie uses this for:
          • Installing the correct package versions for Jinie_main's
            backend before boot, or for a generated project's tooling

        PRE   requirements_file exists on disk
        POST  packages installed into the current interpreter's
              environment; InstallResult returned; an INSTALL entry
              added to the log
        ERR   EnvSetupError(REQUIREMENTS_FILE_NOT_FOUND | INSTALL_FAILED)
        """
        raise NotImplementedError

    def get_log(self) -> list:
        """
        Return snapshot of the internal operation log (list[dict]).
        Logger module (Module 08) reads this for audit events.
        """
        raise NotImplementedError
