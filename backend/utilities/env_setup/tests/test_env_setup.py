"""
backend/utilities/env_setup/tests/test_env_setup.py
======================================================
All tests for EnvSetupManager — unit tests AND the pipeline
boundary test (EnvSetupManager -> FileHandler) live here.

Run:
    cd jinie
    python -m pytest backend/utilities/env_setup/tests/ -v
"""

import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from backend.utilities.env_setup.env_setup          import EnvSetupManager
from backend.utilities.env_setup.env_setup_contract import (
    DependencyReport, DirectoryResult, EnvVarResult, InstallResult,
    EnvSetupError,
)


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def es():
    return EnvSetupManager()


@pytest.fixture
def fake_tools():
    """Deterministic, offline dependency spec for CI runners."""
    return {
        "python": {
            "command":      ["python3", "--version"],
            "min_version":  (3, 0, 0),
            "install_hint": "Install Python 3 from https://python.org",
        },
        "definitely_missing_tool": {
            "command":      ["definitely-missing-tool-xyz", "--version"],
            "min_version":  None,
            "install_hint": "This tool does not exist",
        },
    }


# ═══════════════════════════════════════════════════════════════
# verify_dependencies
# ═══════════════════════════════════════════════════════════════

class TestVerifyDependencies:

    def test_returns_dependency_report(self, es, fake_tools):
        report = es.verify_dependencies(fake_tools)
        assert isinstance(report, DependencyReport)
        assert report.trace_id.startswith("ES-")

    def test_never_raises_on_missing_tool(self, es, fake_tools):
        report = es.verify_dependencies(fake_tools)
        assert report.all_satisfied is False

    def test_missing_tool_has_empty_found_version(self, es, fake_tools):
        report = es.verify_dependencies(fake_tools)
        missing = next(c for c in report.checks
                        if c.name == "definitely_missing_tool")
        assert missing.satisfied is False
        assert missing.found_version == ""
        assert missing.install_hint != ""

    def test_present_tool_is_satisfied(self, es, fake_tools):
        report = es.verify_dependencies(fake_tools)
        present = next(c for c in report.checks if c.name == "python")
        assert present.satisfied is True
        assert present.found_version != ""

    def test_version_too_low_is_not_satisfied(self, es):
        tools = {"python": {"command": ["python3", "--version"],
                             "min_version": (999, 0, 0), "install_hint": "x"}}
        report = es.verify_dependencies(tools)
        assert report.checks[0].satisfied is False

    def test_log_records_call(self, es, fake_tools):
        es.verify_dependencies(fake_tools)
        assert es.get_log()[0]["operation"] == "VERIFY"


# ═══════════════════════════════════════════════════════════════
# create_directories
# ═══════════════════════════════════════════════════════════════

class TestCreateDirectories:

    def test_returns_directory_result(self, es, tmp_path):
        result = es.create_directories(str(tmp_path), ["backend/generated"])
        assert isinstance(result, DirectoryResult)
        assert result.trace_id.startswith("ES-")

    def test_creates_nested_directories(self, es, tmp_path):
        es.create_directories(str(tmp_path), ["backend/generated", "backend/logs"])
        assert (tmp_path / "backend" / "generated").is_dir()
        assert (tmp_path / "backend" / "logs").is_dir()

    def test_existing_directory_reported_as_skipped(self, es, tmp_path):
        (tmp_path / "backend").mkdir()
        result = es.create_directories(str(tmp_path), ["backend"])
        assert any(p.endswith("backend") for p in result.skipped)
        assert result.created == []

    def test_invalid_path_raises(self, es):
        with pytest.raises(EnvSetupError) as exc:
            es.create_directories("", ["x"])
        assert exc.value.code == "INVALID_PATH"

    def test_log_records_call(self, es, tmp_path):
        es.create_directories(str(tmp_path), ["a"])
        assert es.get_log()[0]["operation"] == "CREATE_DIRS"


# ═══════════════════════════════════════════════════════════════
# set_environment_variables
# ═══════════════════════════════════════════════════════════════

class TestSetEnvironmentVariables:

    def test_applies_to_process_environ(self, es):
        es.set_environment_variables({"JINIE_TEST_VAR": "hello"})
        assert os.environ["JINIE_TEST_VAR"] == "hello"
        del os.environ["JINIE_TEST_VAR"]

    def test_rejects_unsafe_keys(self, es):
        result = es.set_environment_variables({
            "VALID_KEY": "1",
            "bad key with spaces": "rejected",
        })
        assert "VALID_KEY" in result.variables_set
        assert "bad key with spaces" in result.variables_skipped
        del os.environ["VALID_KEY"]

    def test_persists_to_file_when_path_given(self, es, tmp_path):
        target = tmp_path / ".env"
        result = es.set_environment_variables(
            {"FIREBASE_PROJECT_ID": "jinie-main-prod"},
            persist_path=str(target),
        )
        assert result.persisted_path == str(target.resolve())
        content = target.read_text(encoding="utf-8")
        assert "FIREBASE_PROJECT_ID=jinie-main-prod" in content
        del os.environ["FIREBASE_PROJECT_ID"]

    def test_no_persist_path_leaves_field_empty(self, es):
        result = es.set_environment_variables({"JINIE_TEST_VAR2": "x"})
        assert result.persisted_path == ""
        del os.environ["JINIE_TEST_VAR2"]

    def test_persist_merges_without_clobbering(self, es, tmp_path):
        target = tmp_path / ".env"
        es.set_environment_variables({"FOO": "1"}, persist_path=str(target))
        es.set_environment_variables({"BAR": "2"}, persist_path=str(target))
        content = target.read_text(encoding="utf-8")
        assert "FOO=1" in content
        assert "BAR=2" in content
        del os.environ["FOO"]
        del os.environ["BAR"]

    def test_log_records_call(self, es):
        es.set_environment_variables({"JINIE_TEST_VAR3": "x"})
        assert es.get_log()[0]["operation"] == "SET_ENV"
        del os.environ["JINIE_TEST_VAR3"]


# ═══════════════════════════════════════════════════════════════
# install_requirements
# ═══════════════════════════════════════════════════════════════

class TestInstallRequirements:

    def test_missing_file_raises(self, es, tmp_path):
        with pytest.raises(EnvSetupError) as exc:
            es.install_requirements(str(tmp_path / "missing_requirements.txt"))
        assert exc.value.code == "REQUIREMENTS_FILE_NOT_FOUND"

    def test_empty_requirements_file_succeeds(self, es, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("", encoding="utf-8")
        result = es.install_requirements(str(req))
        assert isinstance(result, InstallResult)
        assert result.success is True

    def test_comment_only_requirements_file_succeeds(self, es, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("# nothing here yet\n\n", encoding="utf-8")
        result = es.install_requirements(str(req))
        assert result.success is True

    def test_nontrivial_file_invokes_pip_with_correct_args(self, es, tmp_path, monkeypatch):
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\n", encoding="utf-8")

        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            class FakeProc:
                returncode = 0
                stdout = "Successfully installed requests-2.31.0\n"
                stderr = ""
            return FakeProc()

        monkeypatch.setattr("backend.utilities.env_setup.env_setup.subprocess.run", fake_run)
        result = es.install_requirements(str(req))

        assert result.success is True
        assert "-m" in captured["cmd"] and "pip" in captured["cmd"]
        assert str(req.resolve()) in captured["cmd"]

    def test_pip_nonzero_exit_raises_install_failed(self, es, tmp_path, monkeypatch):
        req = tmp_path / "requirements.txt"
        req.write_text("some-package==1.0.0\n", encoding="utf-8")

        def fake_run(cmd, **kwargs):
            class FakeProc:
                returncode = 1
                stdout = ""
                stderr = "ERROR: No matching distribution found\n"
            return FakeProc()

        monkeypatch.setattr("backend.utilities.env_setup.env_setup.subprocess.run", fake_run)
        with pytest.raises(EnvSetupError) as exc:
            es.install_requirements(str(req))
        assert exc.value.code == "INSTALL_FAILED"

    def test_log_records_call(self, es, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("", encoding="utf-8")
        es.install_requirements(str(req))
        assert es.get_log()[0]["operation"] == "INSTALL"


# ═══════════════════════════════════════════════════════════════
# Full pipeline: create_directories -> FileHandler.write -> read back
# ═══════════════════════════════════════════════════════════════

class TestFullPipeline:

    def test_prepare_workspace_then_write_and_read(self, es, tmp_path):
        from backend.utilities.file_handler.file_handler import FileHandler

        es.create_directories(str(tmp_path), ["backend/generated"])
        target_dir = tmp_path / "backend" / "generated"
        assert target_dir.is_dir()

        fh = FileHandler()
        receipt = fh.write(str(target_dir / "ProductCard.tsx"), "export default {};\n")
        assert receipt.success is True

        payload = fh.read(str(target_dir / "ProductCard.tsx"))
        assert "export default" in payload.raw_content
