from dataclasses import dataclass, field


CONTRACT_VERSION = "1.0.0"


@dataclass
class DependencyCheck:
    name: str
    command: str
    found_version: str
    required_version: str
    satisfied: bool
    install_hint: str


@dataclass
class DependencyReport:
    all_satisfied: bool
    checks: list
    trace_id: str


@dataclass
class ScaffoldResult:
    success: bool
    target_path: str
    project_name: str
    created_paths: list
    skipped_paths: list
    trace_id: str
    warnings: list = field(default_factory=list)


@dataclass
class EnvConfigResult:
    path: str
    variables_written: list
    variables_skipped: list
    trace_id: str


class EnvSetupError(Exception):
    CODES = frozenset({
        'INVALID_PROJECT_NAME',
        'TARGET_NOT_EMPTY',
        'PERMISSION_ERROR',
        'INVALID_ENV_KEY',
    })

    def __init__(self, code: str, message: str, path: str = '') -> None:
        if code not in self.CODES:
            raise ValueError(f'Unknown EnvSetupError code: {code!r}')
        self.code = code
        self.path = path
        super().__init__(f'[EnvSetupManager/{code}] {message}  (path={path!r})')


class IEnvSetupManager:

    def verify_dependencies(self, required_tools: dict = None) -> DependencyReport:
        raise NotImplementedError

    def scaffold_project(self, target_path: str, project_name: str,
                          overwrite: bool = False) -> ScaffoldResult:
        raise NotImplementedError

    def configure_environment(self, target_path: str, variables: dict,
                               filename: str = '.env') -> EnvConfigResult:
        raise NotImplementedError

    def get_log(self) -> list:
        raise NotImplementedError

    def reset_log(self) -> None:
        raise NotImplementedError